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
  - 再取所有 `ONGOING` 比赛关联的录像。
  - 使用集合差集排除仍属于其他进行中比赛的录像。
  - 对剩余录像执行 `queryset.update(ongoing_tournament=False)`，再显式补偿相关缓存和排行副作用。

这条路径在比赛结束、重算、数据修复时可能触发大量数据库查询、信号、Redis 操作，容易成为性能瓶颈。

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

## 当前必要接口

### `reveal_videos_for_tournament(tournament)`

用于比赛结束或取消后，将不再属于任何进行中比赛的录像恢复为普通录像。

当前流程：

1. 从 `tournament.videos` 中找候选录像。
2. 排除仍属于其他 `ONGOING` 比赛的录像。
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

- 明确比赛结束、取消、状态回滚时应在哪些入口调用 `reveal_videos_for_tournament`。
- 补充测试：
  - 比赛结束后，上万条录像不逐条触发 `VideoModel.save()`。
  - 录像从比赛恢复普通后，队列缓存恢复。
  - 录像从比赛恢复普通后，经典个人纪录和 pluck 纪录刷新。
