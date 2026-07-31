# tournament 与 videomanager 交互重构计划

本文档记录 `tournament` app 修改 `VideoModel.ongoing_tournament` 时的性能风险和重构计划。比赛逻辑可能一次影响上万条录像，不能依赖逐条 `video.save(update_fields=['ongoing_tournament'])` 触发信号链。

## 当前交互

### 录像创建时

- `tournament.signals.checkin_video_before_create` 在 `VideoModel` 创建前调用 `tournament.utils.video_checkin`。
- `video_checkin` 根据录像内比赛标识判断是否属于正在进行的比赛。
- 如果命中比赛：
  - 设置 `video.ongoing_tournament = True`。
  - 暂存 `_checked_in_tournaments`。
- `tournament.signals.add_created_video_to_checked_tournaments` 在 `VideoModel` 创建后将录像加入对应 `Tournament.videos` 多对多关系。

这个路径只处理单条新上传录像，当前性能风险较低。

### 比赛状态变化或批量刷新时

- `Tournament.videos` 记录录像与比赛的关系。
- `VideoModel.ongoing_tournament` 是一个冗余布尔字段，用于快速屏蔽普通录像队列、个人纪录和排行榜刷新。
- 当前 `tournament.services.reveal_videos_for_tournament` 使用批量逻辑：
  - 先取当前比赛仍标记为 `ongoing_tournament=True` 的录像。
  - 再取所有未公开比赛关联的录像。
  - 使用集合差集排除仍属于其他未颁奖且未取消比赛的录像。
  - 对剩余录像执行 `queryset.update(ongoing_tournament=False)`，再显式补偿相关缓存和排行副作用。

这条路径在比赛颁奖、重算、数据修复时可能触发大量数据库查询、信号、Redis 操作，容易成为性能瓶颈。

## 关键副作用

修改 `VideoModel.ongoing_tournament` 会影响以下系统：

- `videomanager`
  - `ongoing_tournament=True`：录像应从普通状态队列中移除。
  - `ongoing_tournament=False`：录像应按当前 `state` 恢复到对应队列。
  - 当前单条路径由 `videomanager.signals.refresh_state_queue_on_video_save` 处理。
- `msuser`
  - 比赛录像不参与经典个人纪录。
  - 从普通录像进入比赛时，如果该录像是当前纪录，需要重建受影响纪录。
  - 从比赛录像恢复普通录像时，需要尝试吸收到个人纪录。
- `customranking`
  - 比赛录像不参与自定义 pluck 排行。
  - 从普通录像进入比赛时，需要刷新受影响的 `CustomPluckRecord`。
  - 从比赛录像恢复普通录像时，需要尝试吸收到 pluck 纪录。

由于 `queryset.update` 不触发 `VideoModel` 的 `pre_save/post_save`，批量服务必须显式补偿这些副作用。

## 重构目标

- 批量修改 `VideoModel.ongoing_tournament` 时，不逐条调用 `video.save()`。
- 对受影响录像先收集必要信息，再用 `queryset.update` 批量写数据库。
- 对 Redis 队列、经典纪录、自定义 pluck 纪录使用批处理 service 显式刷新。
- 单条上传路径可以继续使用现有信号，但批量路径必须绕开逐条信号。

## `NORMAL` 比赛缓存

`NORMAL` 比赛数量较少，但列表、新闻、录像 checkin 等入口访问频繁，可以使用 Redis 缓存降低数据库查询压力。

缓存 key 固定为：

- `tournament:normal`

缓存使用一个 Redis hash 保存所有 `NORMAL` 比赛的基础信息。hash key 为比赛 id，hash value 为序列化后的比赛信息，例如：

```text
HSET tournament:normal 123 '{"id":123,"series":"gsc","start_time":"...","end_time":"...","order":8,"token":"G12345"}'
```

同一时间只会存在一个 `NORMAL` GSC 比赛，因此不需要额外维护 `order -> tournament_id` 或 `token -> tournament_id` 索引。GSC 录像 checkin 可以直接读取 `tournament:normal` 中的 GSC 项，再比较 token 和时间窗口。

缓存中不存 `PREPARING`、`ONGOING`、`FINISHED` 的拆分结果。它们由调用方根据 `start_time`、`end_time` 和当前时间从 `NORMAL` 比赛动态推导，避免比赛跨过开始或结束时间时依赖定时任务刷新缓存。

缓存中暂不保存参赛选手成绩：

- 比赛期间成绩不公开，运行期维护每个选手的 37 个成绩没有直接用户价值。
- 比赛结束时已有后台任务刷新 GSC 成绩和排名，可以在结束流程中统一落库。
- 不在比赛期间维护成绩缓存，可以避免每次录像 checkin、录像更新、成绩变化时同步更新 Redis hash/zset，降低写路径复杂度。

如果未来需要比赛期间展示实时榜，可以再单独设计每个比赛的成绩缓存，例如使用 hash 存三组成绩数组、zset 存总成绩：

- `tournament:normal:gsc:{tournament_id}:scores`
- `tournament:normal:gsc:{tournament_id}:rank`

但当前阶段不实现这部分。

`tournament:normal` 应由写路径维护同步。比赛创建、修改 `start_time/end_time/order/token`、验证、取消和颁奖时，在事务提交后对对应比赛执行 `TournamentCache.update_tournament` 或 `TournamentCache.remove_tournament`。读取路径只读取缓存，不在未命中时查询 DB 或重建缓存；缓存与 DB 不同步属于写路径维护 bug。

如果服务器故障、Redis 数据丢失或缓存被手动清空，可以使用 `manage.py rebuild_tournament_cache` 从数据库重建 `tournament:normal` 和 `tournament:normal:participants`。

## `TournamentParticipant` checkin 缓存计划

录像 checkin 还会频繁查询 `TournamentParticipant`，尤其是：

- AVF：根据 `user` 和 `arbiter_identifier` 找到参赛关系。
- GSC/EVF：根据 `user` 和当前 `NORMAL` GSC 比赛判断是否已有参赛关系。

后续可以为当前 `NORMAL` 比赛维护参赛关系缓存，用于快速 checkin。缓存只保存 checkin 需要的最小字段：

- `token`
- `arbiter_identifier`
- `tournament`

不缓存选手成绩、排名、用户展示信息、录像列表。

根据 checkin 查询需求，使用单个 Redis hash 保存所有用户的参赛关系列表。hash key 固定，hash field 为 `user_id`，hash value 为该用户名下所有当前 `NORMAL` 比赛参赛关系的列表，列表项只包含上述三个字段：

```text
HSET tournament:normal:participants {user_id} '[{"token":"G12345","arbiter_identifier":"arbiter-id","tournament":123}]'
```

因为 `NORMAL` 比赛数量较少，单个用户名下的当前参赛关系列表也会很短。AVF checkin 可以读取该用户的列表后按 `arbiter_identifier` 匹配；GSC/EVF checkin 可以读取同一列表后按 `tournament` 判断是否已有参赛关系。

GSC/EVF 路径优先使用 `tournament:normal` 找到唯一 `NORMAL` GSC 比赛，再从 `tournament:normal:participants` 的 `{user_id}` field 判断该用户是否已经存在该比赛的参赛关系。未命中时再创建 `GSCParticipant` 并更新缓存。

缓存失效或更新策略：

- `TournamentParticipant` / `GSCParticipant` 创建、修改、删除后，在对应用户的列表缓存中同步 upsert 或 delete 该参赛关系。
- checkin 读路径只读取缓存，不在未命中时查询 DB 或重建缓存；缓存与 DB 不同步属于写路径维护 bug。
- `TournamentCache.remove_tournament` 移除 `tournament:normal` 中的比赛时，也会从 `tournament:normal:participants` 的所有用户列表中精确移除对应比赛的参赛关系，避免已结束或已取消比赛继续参与 checkin。
- 失效应尽量在事务提交后执行。

## 当前必要接口

### `reveal_videos_for_tournament(tournament)`

用于比赛颁奖后，将不再属于任何未颁奖且未取消比赛的录像恢复为普通录像。

当前流程：

1. 从 `tournament.videos` 中找候选录像。
2. 排除仍属于其他未颁奖且未取消比赛的录像。
3. 只处理 `ongoing_tournament=True` 的录像。
4. 固化受影响录像 id。
5. 批量执行：
   - `VideoModel.objects.filter(id__in=ids).update(ongoing_tournament=False)`。
6. 显式补偿：
   - 按当前 `state` 将录像批量恢复到 `videomanager` 普通队列。
   - `msuser` 尝试将这些录像吸收到经典个人纪录。
   - `customranking` 尝试将这些录像吸收到自定义 pluck 纪录。

## 暂不实现的接口

- `hide_videos_for_tournament(tournament)` 暂非必要。
  - 新上传录像仍由当前单条 `video_checkin` 路径处理。
  - 如果未来需要补录或批量隐藏比赛录像，再按同样原则设计批处理。
- `refresh_ongoing_tournament_for_range(start_id, end_id)` 暂非必要。
  - 数据修复需求出现后再实现分段重算。

## videomanager 批量缓存需求

`videomanager.cache.VideoQueueCache` 已具备以下批量方法：

- `add_bulk(videos)`：批量写入队列。
- `update_bulk(videos)`：只更新已存在于队列中的项。
- `remove_bulk(videos)`：批量从队列删除。

`videomanager.cache` 已提供按状态分组的批量 helper：

- `add_videos_to_state_queues_bulk(videos)`

这个 helper 集中维护 `state -> queue` 映射，避免 `tournament` 直接复制 `videomanager.signals.STATE_QUEUE_NAMES`。

## msuser 批量刷新需求

已有可复用能力：

- `get_current_record_keys_for_video_ids(userms, video_ids)`
- `rebuild_personal_records(user, record_keys)`
- `update_personal_records_from_videos(userms, videos)`

新增批量能力：

- `update_personal_records_from_video_queryset(videos)`。
  - 输入受影响录像 queryset。
  - 按 `player_id` 分组。
  - `True -> False` 时，对每个用户吸收新增普通录像。

## customranking 批量刷新需求

已有可复用能力：

- `add_videos_to_custom_pluck_ranks(videos)`
- `remove_videos_from_custom_pluck_ranks(video_ids)`

这些函数可直接用于 `ongoing_tournament` 批量切换后的补偿。

## 待处理问题

- 明确比赛取消、状态回滚时应在哪些入口调用 `reveal_videos_for_tournament`。
- 补充测试：
  - 比赛颁奖后，上万条录像不逐条触发 `VideoModel.save()`。
  - 录像从比赛恢复普通后，队列缓存恢复。
  - 录像从比赛恢复普通后，经典个人纪录和 pluck 纪录刷新。
