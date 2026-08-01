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

`Tournament` 父表增加了 `subclass` 字段，用于快速定位具体子类。当前线上只有 `GSCTournament`，所以字段默认值暂时为 `g`，迁移后既有比赛都会被视为 GSC。后续新增比赛类型时，应先扩展 `Tournament_TextChoices.Subclass`，再在模型层的子类定向 helper 中补充查询逻辑，避免依赖泛化的 `select_subclasses()`。缓存层不负责父类到子类的定向，只接收已经定向完成的具体比赛对象。

缓存 key 固定为：

- `tournament:normal`

缓存使用一个 Redis hash 保存所有 `NORMAL` 比赛的基础信息。hash key 为比赛 id，hash value 为序列化后的比赛信息，例如：

```text
HSET tournament:normal 123 '{"id":123,"series":"gsc","start_time":"...","end_time":"...","order":8,"token":"G12345"}'
```

同一时间只会存在一个 `NORMAL` GSC 比赛，因此不需要额外维护 `order -> tournament_id` 或 `token -> tournament_id` 索引。录像 checkin 不通过 `tournament:normal` 判断时间窗口；它只使用 participant 缓存中的参赛关系窗口。

缓存中不存 `PREPARING`、`ONGOING`、`FINISHED` 的拆分结果。它们由调用方根据 `start_time`、`end_time` 和当前时间从 `NORMAL` 比赛动态推导，避免比赛跨过开始或结束时间时依赖定时任务刷新缓存。

缓存中暂不保存参赛选手成绩：

- 比赛期间成绩不公开，运行期维护每个选手的 37 个成绩没有直接用户价值。
- 比赛结算后台任务会统一刷新 GSC 成绩和排名，并在结束流程中落库。
- 不在比赛期间维护成绩缓存，可以避免每次录像 checkin、录像更新、成绩变化时同步更新 Redis hash/zset，降低写路径复杂度。

GSC 成绩刷新由 `tournament.gsc.services.refresh_gsc_scores` 负责。当前实现按初级、中级、高级分别执行查询，每个级别只取每个玩家按 `timems` 排序的前 N 条有效录像；三个级别的结果先在内存中按用户合并，最后统一计算 participant 的完整成绩并使用一次 `bulk_update` 分批落库。这样避免单个大查询同时处理所有级别，也避免每个级别分别保存 participant。

GSC 只保留比赛结算后台任务，不再提供单独的刷新成绩后台任务。`GSCTournament.task` 指向当前结算任务；创建新结算任务前会复用仍处于 READY/RUNNING 的任务，避免管理员重复点击时产生重复结算任务。

如果未来需要比赛期间展示实时榜，可以再单独设计每个比赛的成绩缓存，例如使用 hash 存三组成绩数组、zset 存总成绩：

- `tournament:normal:gsc:{tournament_id}:scores`
- `tournament:normal:gsc:{tournament_id}:rank`

但当前阶段不实现这部分。

`tournament:normal` 应由写路径维护同步。比赛创建、修改 `start_time/end_time/order/token`、验证、取消和颁奖时，在事务提交后对对应比赛执行 `TournamentCache.update_tournament` 或 `TournamentCache.remove_tournament`。读取路径只读取缓存，不在未命中时查询 DB 或重建缓存；缓存与 DB 不同步属于写路径维护 bug。

Redis 中仍保存 JSON object/list，由 `dataclass-json` 负责序列化和反序列化；时间字段使用该库默认的 timestamp 表示。Python 读取后应统一反序列化为 dataclass，例如 `CachedNormalTournament` 和 `CachedNormalParticipant`，调用方使用属性访问以获得类型提示，不再在业务代码中传递裸 dict。

比赛审核通过的前置条件是 `start_time` 和 `end_time` 都已经确定，且 `start_time < end_time`。时间缺失或时间范围非法时，`Tournament.validate()` 应返回失败，入口不能把比赛切换到 `NORMAL`，GSC 也不能生成 token。

因此正常写路径下，`tournament:normal` 和 `tournament:normal:participants` 中的 `start_time/end_time` 都应视为必填字段。Python dataclass 类型不再把这两个字段标记为可空，checkin 时间窗口判断也不需要处理缺失时间；如果缓存中出现缺失时间，应视为缓存写路径 bug，通过修复写路径或重建缓存处理。

GSC 创建 `GSCParticipant` 时，participant 自身的 `start_time/end_time` 应与对应 `GSCTournament.start_time/end_time` 完全一致。`TournamentParticipant.start_time` 使用 `default=timezone.now` 仅服务于非 GSC 或未显式传值的普通创建路径；GSC 写路径必须显式传入比赛时间窗口。

如果服务器故障、Redis 数据丢失或缓存被手动清空，可以使用 `manage.py rebuild_tournament_cache` 从数据库重建 `tournament:normal` 和 `tournament:normal:participants`。

## `TournamentParticipant` checkin 缓存计划

录像 checkin 还会频繁查询 `TournamentParticipant`，尤其是：

- AVF：根据 `user` 和 `arbiter_identifier` 找到参赛关系。
- 非 AVF：根据 `user` 和录像内 token 找到参赛关系。用户必须先显式创建 `GSCParticipant`，录像 checkin 不再因为命中 GSC token 自动创建 participant。

当前已开始为 `NORMAL` 比赛维护参赛关系缓存，用于快速 checkin。缓存只保存 checkin 需要的最小字段：

- `id`
- `token`
- `arbiter_identifier`
- `tournament`
- `start_time`
- `end_time`

不缓存选手成绩、排名、用户展示信息、录像列表。

根据 checkin 查询需求，使用单个 Redis hash 保存所有用户的参赛关系列表。hash key 固定，hash field 为 `user_id`，hash value 为该用户名下所有当前 `NORMAL` 比赛参赛关系的列表，列表项只包含上述三个字段：

```text
HSET tournament:normal:participants {user_id} '[{"id":456,"token":"G12345","arbiter_identifier":"arbiter-id","tournament":123,"start_time":"...","end_time":"..."}]'
```

因为 `NORMAL` 比赛数量较少，单个用户名下的当前参赛关系列表也会很短。AVF checkin 可以读取该用户的列表后按 `arbiter_identifier` 匹配；非 AVF checkin 可以读取同一列表后按 `token` 匹配，GSC participant 的 token 固定为对应 GSC token。匹配到候选 participant 后，统一使用 `video.upload_time` 与 participant 自身的 `start_time/end_time` 比较，判断录像是否在该参赛关系的有效窗口内。

录像 checkin 路径不再用 tournament 的当前状态或 tournament 的当前时间窗口做二次判断，也不创建 participant。`TournamentCache.checkin_arbiter` / `checkin_token` 返回的应是已经通过 `upload_time` 与 participant 时间窗口匹配的参赛关系。

缓存失效或更新策略：

- `TournamentParticipant` / `GSCParticipant` 创建、修改、删除后，在对应用户的列表缓存中同步 upsert 或 delete 该参赛关系。
- `TournamentParticipant` / `GSCParticipant` 创建后，在事务提交后扫描同一用户 `upload_time` 落在 participant `start_time/end_time` 窗口内的既有录像，并补充写入 `Tournament.videos` 多对多关系。AVF 录像要求 `ExpandVideoModel.identifier == participant.arbiter_identifier`；其他录像要求 `ExpandVideoModel.tournament_identifier` 包含 participant token。这个补偿只维护比赛-录像关系，不修改 `VideoModel.ongoing_tournament`。
- `finish_gsc_tournament` 开头会调用通用服务 `delete_participants_without_videos` 删除没有任何本比赛录像的站内 participant；当前只有 GSC 结束流程使用这个通用服务。
- checkin 读路径只读取缓存，不在未命中时查询 DB 或重建缓存；缓存与 DB 不同步属于写路径维护 bug。
- `TournamentCache.remove_tournament` 移除 `tournament:normal` 中的比赛时，也会从 `tournament:normal:participants` 的所有用户列表中精确移除对应比赛的参赛关系，避免已结束或已取消比赛继续参与 checkin。
- 失效应尽量在事务提交后执行。

当前重构状态：

- `TournamentCache` 已开始封装比赛和参赛关系缓存读写，包括 `get_tournament`、`get_tournament_all`、`get_gsc`、`get_participant_list`、`set_participant_list`、`update_participant`、`remove_participant`、`checkin_arbiter` 和 `checkin_token`，读取结果已改为 dataclass。
- `tournament.services.checkin_with_arbiter` / `checkin_with_token` 正在接管 `tournament.utils.video_checkin` 中的 checkin 判定。
- `video_checkin` 在 `VideoModel.pre_save` 阶段运行，此时新录像还没有主键；service 层只返回命中的比赛列表，由 `video_checkin` 暂存到 `_checked_in_tournaments`，再由 `post_save` 写入 `Tournament.videos` 多对多关系。
- EVF 路径在没有参赛缓存时直接跳过 checkin；用户需要先通过 GSC 注册接口显式创建 participant。
- `serialize_normal_participant` 应继续兼容 `arbiter_identifier=None` 的参赛关系，因为 GSC participant 只依赖固定 token。

当前已重新运行 `python -m flake8 tournament` 和 `manage.py test tournament --keepdb`。后端检查通过，测试套件 24 个用例通过。

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
