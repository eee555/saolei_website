# tournament 与 videomanager 交互重构计划

本文档记录 `tournament` app 修改 `VideoModel.ongoing_tournament` 时的性能风险和重构计划。比赛逻辑可能一次影响上万条录像，不能依赖逐条 `video.save(update_fields=['ongoing_tournament'])` 触发信号链。

## 当前交互

### 录像创建时

- `tournament.signals.checkin_video_before_create` 在 `VideoModel` 创建前根据 `video.video.identifier` 或 `video.video.tournament_identifier` 判断是否属于正在进行的比赛。
- 如果命中比赛：
  - 设置 `video.ongoing_tournament = True`。
  - 暂存 `_checked_in_tournaments`，供创建后写入 M2M 使用。
- `tournament.signals.add_created_video_to_checked_tournaments` 在 `VideoModel` 创建后消费 `_checked_in_tournaments`，将录像加入对应 `Tournament.videos` 多对多关系。

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

## `NORMAL` 比赛缓存

`NORMAL` 比赛数量较少，但列表、新闻、录像 checkin 等入口访问频繁，可以使用 Redis 缓存降低数据库查询压力。

`Tournament` 父表增加了 `subclass` 字段，用于快速定位具体子类。早期迁移时字段默认值暂时为 `g`，既有比赛都会被视为 GSC；新增周赛后，`Tournament_TextChoices.Subclass.WEEKLY` 与 `Tournament.select_subclass()` 已能指向 `WeeklyTournament`。当前所有业务接口只接受 GSC 和周赛，因此条件判断统一按 “GSC / 否则周赛” 处理，不保留第三类比赛 fallback。后续新增比赛类型时，应先扩展 `Tournament_TextChoices.Subclass`，再补充对应分支。信号层不负责父类到子类的定向，`TournamentCache.update_tournament` 内部会先调用 `select_subclass()`，再序列化具体比赛对象。

缓存 key 固定为：

- `tournament:normal`

缓存使用一个 Redis hash 保存所有 `NORMAL` 比赛的基础信息。hash key 为比赛 id，hash value 为序列化后的比赛信息。缓存只保存父类通用字段、`subclass` 和一个 `data` 字段；子类独占字段统一放入 `data`，前后端都根据 `subclass/data` 转换出展示用的 `name`、`description` 等字段。例如：

```text
HSET tournament:normal 123 '{"id":123,"state":"n","subclass":"g","host_id":null,"start_time":...,"end_time":...,"data":{"order":8,"token":"G12345"}}'
HSET tournament:normal 456 '{"id":456,"state":"n","subclass":"w","host_id":null,"start_time":...,"end_time":...,"data":{"year":2026,"week":12,"tournament_format":"c"}}'
```

同一时间只会存在一个 `NORMAL` GSC 比赛，因此不需要额外维护 `order -> tournament_id` 或 `token -> tournament_id` 索引。录像 checkin 不通过 `tournament:normal` 判断时间窗口；它只使用 participant 缓存中的参赛关系窗口。

缓存中不存 `PREPARING`、`ONGOING`、`FINISHED` 的拆分结果。它们由调用方根据 `start_time`、`end_time` 和当前时间从 `NORMAL` 比赛动态推导，避免比赛跨过开始或结束时间时依赖定时任务刷新缓存。

缓存中暂不保存参赛选手成绩：

- 比赛期间成绩不公开，运行期维护每个选手的 37 个成绩没有直接用户价值。
- 比赛结算后台任务会统一刷新 GSC 成绩和排名，并在结束流程中落库。
- 不在比赛期间维护成绩缓存，可以避免每次录像 checkin、录像更新、成绩变化时同步更新 Redis hash/zset，降低写路径复杂度。

GSC 成绩刷新由 `tournament.gsc.services.refresh_gsc_scores` 负责。当前实现按初级、中级、高级分别执行查询，每个级别只取每个玩家按 `timems` 排序的前 N 条有效录像；三个级别的结果先在内存中按用户合并，最后统一计算 participant 的完整成绩并使用一次 `bulk_update` 分批落库。这样避免单个大查询同时处理所有级别，也避免每个级别分别保存 participant。

`GSCParticipant.t37` 是持久化的 generated field，等于 `bt20sum + it12sum + et5sum`，并建立 `gsc_t37_idx` 索引用于 GSC 排名和历史最好成绩查询。Python 侧在设置三个 sum 字段时会同步临时更新实例上的 `t37`，供保存信号在不重新读取 participant 的情况下增量比较 best。

GSC 只保留比赛结算后台任务，不再提供单独的刷新成绩后台任务。`GSCTournament.task` 指向当前结算任务；创建新结算任务前会复用仍处于 READY/RUNNING 的任务，避免管理员重复点击时产生重复结算任务。

TODO: 如果未来需要比赛期间展示实时榜，可以再单独设计每个比赛的成绩缓存，例如使用 hash 存三组成绩数组、zset 存总成绩：

- `tournament:normal:gsc:{tournament_id}:scores`
- `tournament:normal:gsc:{tournament_id}:rank`

但当前阶段不实现这部分。

`tournament:normal` 应由写路径维护同步。比赛创建、修改 `start_time/end_time/order/token`、验证、取消和颁奖时，在事务提交后对对应比赛执行 `TournamentCache.update_tournament` 或 `TournamentCache.remove_tournament`。读取路径只读取缓存，不在未命中时查询 DB 或重建缓存；缓存与 DB 不同步属于写路径维护 bug。`get_tournament_list(category="normal")` 已直接返回 `TournamentCache.get_tournament_all()`，因此 NORMAL 首页列表不会触发子类查询。

删除 GSC 时不需要监听 `GSCTournament.post_delete`；Django 多表继承删除子表时会级联删除父表，缓存清理由 `Tournament.post_delete` 统一处理。`TournamentCache.remove_tournament` 固定接收 `tournament_id: int`。由于 `post_delete` 的 `on_commit` 回调执行时 model instance 的主键可能已经被清空，信号里应先捕获 `tournament_id`，再传给 `TournamentCache.remove_tournament`。

Redis 中仍保存 JSON object/list，由 `dataclass-json` 负责序列化和反序列化；时间字段使用该库默认的 timestamp 表示。Python 读取后应统一反序列化为 dataclass，例如 `CachedTournament`、`CachedGSCTournament`、`CachedWeeklyTournament` 和 `CachedNormalParticipant`，调用方使用属性访问以获得类型提示，不再在业务代码中传递裸 dict。

比赛审核通过的前置条件是 `start_time` 和 `end_time` 都已经确定，且 `start_time < end_time`。时间缺失或时间范围非法时，`Tournament.validate()` 应返回失败，入口不能把比赛切换到 `NORMAL`，GSC 也不能生成 token。

因此正常写路径下，`tournament:normal` 和 `tournament:normal:participants` 中的 `start_time/end_time` 都应视为必填字段。Python dataclass 类型不再把这两个字段标记为可空，checkin 时间窗口判断也不需要处理缺失时间；如果缓存中出现缺失时间，应视为缓存写路径 bug，通过修复写路径或重建缓存处理。

GSC 创建 `GSCParticipant` 时，participant 自身的 `start_time/end_time` 应与对应 `GSCTournament.start_time/end_time` 完全一致。`TournamentParticipant.start_time` 使用 `default=timezone.now` 仅服务于非 GSC 或未显式传值的普通创建路径；GSC 写路径必须显式传入比赛时间窗口。

如果服务器故障、Redis 数据丢失或缓存被手动清空，可以使用 `manage.py rebuild_tournament_cache` 从数据库重建 `tournament:normal` 和 `tournament:normal:participants`。

## 周赛当前状态与 TODO

周赛已经有模型和服务草稿，但还不是完整可用功能。当前设计沿用 `Tournament` / `TournamentParticipant` 的多表继承：`WeeklyTournament` 表示周赛本体，`WeeklyParticipant` 表示单个用户在某场周赛中的 2 高 5 中成绩。

当前已有：

- 模型：`WeeklyTournament` 保存 `year`、`week`、`tournament_format`，`subclass` 为 `Tournament_TextChoices.Subclass.WEEKLY`，名称由年份和周数动态生成。
- 模型：`WeeklyParticipant` 保存 `classic_et`、`classic_it` 和 `classic_score`，并在 `classic_score` 上建索引用于排名查询。
- 服务：`refresh_weekly_classic_scores` 从 `Tournament.videos` 中按用户分别取 2 条高级、5 条中级有效录像，合并后批量更新 `WeeklyParticipant` 的成绩字段。
- 服务：通用 `refresh_tournament_ranks` 按具体比赛的 `order_by` 字段刷新排名，只写入 `rank`；`rank_score` 由统一积分发放服务根据 `Tournament.weight / rank` 写入。
- 任务：`task_weekly_finish` 已串联删除无录像 participant、读取本场 `TournamentUser`、刷新成绩、刷新排名、切换 `AWARDED`、公开录像；排名积分发放和 best 刷新作为非关键后台任务单独派发。
- API：`tournament.weekly.api` 已挂载到 `/api/tournament/weekly/`，当前已有 `POST /new`、`POST /set`、`GET /results` 和 `POST /participant`；进行中比赛的参赛者信息通过通用 `GET /api/tournament/participants` 获取。
- API：`POST /api/tournament/weekly/new` 由 staff 创建下周周赛，参数只包含 `tournament_format`；服务端计算下周 `year/week/start_time/end_time`，`weight=50`，`host=request.user`，禁止重复创建，并在创建后直接 `validate()` 切换到 `NORMAL`。
- API：`POST /api/tournament/weekly/set` 只允许主办方或管理员修改周赛状态，不修改 `year/week/tournament_format`。
- 周赛由网站管理员主办，不在 `WeeklyTournament` 上保存任务引用；管理员通过通用后台任务系统直接管理 `task_weekly_finish`。

周赛后端缓存已经使用 `CachedTournament` 作为基础 dataclass，并通过 `CachedGSCTournament` / `CachedWeeklyTournament` 子类收敛 `data` 的类型。dataclass 子类新增字段时仍需要单独加 `@dataclass`，实际执行 JSON 序列化/反序列化的子类也单独加 `@dataclass_json`。

前后端不再使用比赛 `series` 属性做兼容判断；比赛类型统一由 `subclass` 决定。

## 比赛积分系统

`vitepress_doc/guide/tournament.md` 已定义比赛积分的用户侧规则：比赛结束后发放排名积分和奖金积分；排名积分按 `比赛权重 / 排名` 计算；用户当前积分按 2 年半衰期衰减。`TournamentUser` 已有模型草稿，用于保存用户比赛积分汇总。

当前实现：

- `TournamentUser.score_current` 使用 `FloatField` 保存带时间衰减的当前积分。
- `TournamentUser.last_updated` 表示上次完成积分衰减并写回的时间。
- `score_total`：所有比赛历史累计积分，不参与衰减，用于展示历史贡献。
- `gsc_total` / `weekly_total`：按比赛类型拆分的历史累计积分，不参与衰减；`weekly_classic_total` 是周赛经典模式的累计积分。
- `gsc_best` / `weekly_classic_best` 使用整数打包“最好成绩 + 比赛届数/期数”。GSC 后三位保存届数；周赛经典模式后五位保存 `year % 1000 * 100 + week`。GSC 和周赛经典模式都按“成绩越小越好，同成绩比赛编号越小越好”比较；没有有效历史成绩时使用 `MAX_TOURNAMENT_BEST` 作为哨兵值。
- `tournament.gsc.utils.gsc_encode_best` 和 `tournament.weekly.utils.weekly_encode_best` 分别维护 GSC / 周赛 best 编码。
- `TournamentCache` 使用 Redis sorted set 维护 7 个用户积分排行榜，member 统一为 `user_id`：`tournament:user:score_current`、`tournament:user:score_total`、`tournament:user:gsc_total`、`tournament:user:gsc_best`、`tournament:user:weekly_total`、`tournament:user:weekly_classic_total` 和 `tournament:user:weekly_classic_best`。
- Redis zset 的 score 直接使用对应 `TournamentUser` 字段值。积分字段越大排名越靠前，读取方应使用倒序；best 字段越小成绩越好，读取方应使用正序。
- 默认值不写入排行榜：`score_current`、`score_total`、`gsc_total`、`weekly_total`、`weekly_classic_total` 为 `0` 时从对应 zset 删除；`gsc_best`、`weekly_classic_best` 为 `MAX_TOURNAMENT_BEST` 时从对应 zset 删除。
- 站内用户创建 `TournamentParticipant` / `GSCParticipant` / `WeeklyParticipant` 时，保存信号会在当前数据库事务内立即创建缺失的 `TournamentUser`。删除 participant 不会跟随删除 `TournamentUser`。
- 结束结算的第一步是删除无录像 participant。排名积分发放和 best 刷新任务会从本场剩余站内 participant 出发，通过 `participant.user.tournamentuser` 取得对应的 `TournamentUser`；查询时使用 `select_related('user__tournamentuser')` 避免 N+1。
- `tournament.services.award_tournament_rank_scores` 是统一排名积分发放入口。它先按比赛 `end_time` 衰减所有已有 `TournamentUser.score_current`，再根据 `Tournament.subclass` 读取本场有站内用户且有 `rank` 的具体 participant，按 `round(tournament.weight / participant.rank)` 计算目标排名积分。这个步骤只更新 `score_current`、total 字段和 `TournamentParticipant.rank_score`，不刷新 best，也不隐式创建 `TournamentUser`。
- `TournamentParticipant.rank_score` 记录该 participant 已发放的排名积分。重复结算或重算时按 `target_rank_score - participant.rank_score` 计算增量，避免重复累加；落库时不筛选字段是否发生变化，候选 participant 和对应 `TournamentUser` 会统一 `bulk_update`。
- `tournament.gsc.services.update_gsc_best` / `tournament.weekly.services.update_weekly_best` 在 `GSCParticipant` / `WeeklyParticipant` 保存后，只把当前 participant 成绩与原 best 比较，只有更好时才写入 best，不扫描用户所有历史成绩。
- `tournament.gsc.services.refresh_gsc_best_scores` / `tournament.weekly.services.refresh_weekly_best_scores` 是单场比赛的 best 刷新入口。结算流程使用 `bulk_update` 写入 `rank_score`，不会触发 participant 保存信号，因此 best 刷新作为非关键后台任务显式执行；刷新时同样不筛选字段是否发生变化，统一写回候选用户的 best 字段。best 与排名积分发放没有顺序依赖。
- `award_tournament_rank_scores`、`refresh_gsc_best_scores`、`refresh_weekly_best_scores` 和 `refresh_tournament_user_stats` 在 `TournamentUser` 写库后会同步刷新相应的 Redis zset。participant 保存/删除信号触发的单条 best 更新也会同步刷新对应 best zset。
- `tournament.gsc.signals` / `tournament.weekly.signals` 分别处理 GSC / 周赛 participant 保存与删除后的 best 更新；保存时只比较当前 participant，删除时调用 `calculate_gsc_best_score` / `calculate_weekly_classic_best` 重算该类型历史最好成绩。
- `TournamentUser` 是数据库持久化汇总，不是缓存。participant 信号触发的 `TournamentUser` 更新必须在当前数据库事务内立即执行，不能延迟到 `transaction.on_commit`，从而保证 participant 与汇总字段一起提交或一起回滚。
- `manage.py refresh_tournament_user_stats` 可从所有已发放 `rank_score` 的 participant 重建 `score_total`、`gsc_total`、`weekly_total`、`weekly_classic_total`、`gsc_best` 和 `weekly_classic_best`。命令内部先调用 `tournament.services.refresh_tournament_user_total_fields`，再执行命令内的 best 重建步骤，total 与 best 是两个独立刷新步骤。`score_current` 依赖时间衰减，是实时值，命令不会刷新它。`gsc_best` / `weekly_classic_best` 默认值从 `0` 改为 `MAX_TOURNAMENT_BEST` 后，既有历史行需要通过这个命令修复。
- `manage.py rebuild_tournament_user_cache` 只重建 Redis 排行缓存，不修改数据库；它会从当前 `TournamentUser` 表读取所有字段，包括不由 `refresh_tournament_user_stats` 重算的 `score_current`。
- GSC / 周赛 finish 任务在刷新成绩和排名后切换 `AWARDED` 并公开录像；随后派发 `task_award_tournament` 和对应的 best 刷新任务。排名积分发放和 best 刷新都属于非关键后台任务，失败后可以单独重跑。
- GSC / 周赛结算链路使用 `tournament` logger 写入 `logs/tournament.log`。日志覆盖后台任务创建/复用、任务开始/失败/完成、删除无录像 participant、读取 `TournamentUser`、刷新成绩、刷新排名、发放 `rank_score`、刷新 best、状态切换和公开录像等阶段，并记录每个阶段的处理数量。
- 无站内用户的 participant 不会创建 `TournamentUser`。

当前测试覆盖：

- `TournamentUser` 默认值和 best 编码/解码 helper。
- 积分衰减公式、按 `rank_score` 计算增量、`last_updated` 写回。
- GSC / 周赛结算后正确写入 `TournamentUser`。
- GSC / 周赛 participant 保存或删除后，信号刷新历史最好成绩。
- 管理命令可重建历史 total/best 字段，且不会修改 `score_current` / `last_updated`。
- 重复执行结算流程不会重复发放积分。
- 无录像 participant 在结算开头被删除后不会获得积分。

TODO: 奖金积分暂不实现，但需要预留设计：

- 奖金积分以后使用单独字段或单独发放记录，不进入 `rank_score`。
- 奖金金额与积分的换算规则、币种和管理员录入入口仍是争议核心，暂无结论。
- 在用户文档中继续标记“暂不支持”，直到后端和前端都完成。

TODO: 补充积分展示 API 与前端：

先不急着做，等结构继续设计。

- 用户资料页需要展示当前比赛积分、历史总积分、GSC/周赛拆分积分和最好成绩。
- 比赛积分排行榜需要分页 API；如果访问频繁，应设计 Redis 缓存或类似 `userprofile` 的 IndexedDB 同步方案。
- `TournamentUser` 更新后如果影响用户资料摘要，需要同步考虑 `userprofile` 缓存/批量接口的失效策略。

## TODO: 历史比赛列表同步计划

当前通用接口 `get_tournament_list` 会尝试返回所有比赛的完整信息。随着历史比赛数量增加，这个接口会同时遇到两个问题：

- 返回全量历史比赛本身不适合作为长期接口形态。
- 完整比赛信息需要根据 `Tournament.subclass` 组装具体子类数据，直接逐条定向会造成 N+1 查询。

TODO: 这类列表展示问题优先参考 `userprofile` app 的缓存同步方式解决，而不是优先重构 Django 多表继承实现。前端应把比赛基础信息缓存在 IndexedDB 中，后端提供列表索引、批量详情和更新检查接口。

推荐接口形态：

- TODO: `GET /api/tournament/list`
  - 返回用于当前列表页的轻量索引，长期应支持分页、状态过滤、系列过滤和排序。
  - 响应只包含 `id`、必要排序字段和可选的 `date_updated`，不负责返回完整 `TournamentInfo`。
- TODO: `GET /api/tournament/infobulk?ids=1,2,3`
  - 按 id 批量返回完整 `TournamentInfo`。
  - 后端可以在这个小批量范围内处理子类定向；短期即使仍使用单条定向，压力也远小于全量列表。
- TODO: `GET /api/tournament/infoupdated?since=123456789`
  - 返回自指定时间戳以来发生变化的比赛 id，用于前端删除 IndexedDB 中的过期缓存。

TODO: 为支持更新检查，`Tournament` 父表需要增加类似 `UserProfile.date_updated` 的 `DateTimeField(auto_now=True)`。如果 GSC 子表字段变化会影响 `TournamentInfo`，写路径必须同步触发父表更新时间更新。例如 `order`、`token`、`start_time`、`end_time`、`state`、`host` 等字段变化后，前端缓存应能通过 `infoupdated` 感知。

TODO: 前端实现可以复用 `userService.ts` 的设计：

- 新增 IndexedDB store，例如 `tournament-info`，主键为 `id`，row schema 与 `TournamentInfo` 保持一致。
- `fetchTournament(id)` 优先读取 IndexedDB，缓存缺失时进入批量请求队列。
- 同一 tick 或短延迟窗口内的多个缺失 id 合并为一次 `infobulk` 请求。
- 按配置周期请求 `infoupdated`，删除已更新比赛的本地缓存；首次 `lastUpdate=0` 时直接清空本地比赛缓存，避免请求全量更新 id。
- IndexedDB 不可用时降级为网络请求。

TODO: 迁移后，`get_tournament_list` 可以逐步退化为轻量索引接口，或由新的 `/list` 接口替代。完整比赛信息只在用户实际需要展示对应比赛时通过 `infobulk` 获取。模型层的子类定向问题因此被限制在小批量详情接口内部，不再成为全量列表的性能瓶颈。

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

- `TournamentParticipant` / `GSCParticipant` 创建、修改后，在对应用户的列表缓存中同步 upsert 该参赛关系。participant 保存信号用两个 `post_save` 装饰器绑定到同一个 `update_cache_on_participant_save` 接收器；父类和 GSC 子类保存都进入同一套逻辑，只在缓存相关字段变化时更新缓存，GSC 子类成绩字段变化不会刷新 participant 缓存。
- `TournamentParticipant` 创建后，立即扫描同一用户 `upload_time` 落在 participant `start_time/end_time` 窗口内的既有录像，并补充写入 `Tournament.videos` 多对多关系。AVF 录像要求 `ExpandVideoModel.identifier == participant.arbiter_identifier`；其他录像要求 `ExpandVideoModel.tournament_identifier` 包含 participant token。这个补偿只维护比赛-录像关系，不修改 `VideoModel.ongoing_tournament`。这里不能延迟到 `transaction.on_commit`，因为创建 participant 的调用方可能需要在同一事务内继续依赖补录后的比赛-录像关系。
- GSC / 周赛 finish 任务开头会调用通用服务 `delete_participants_without_videos` 删除没有任何本比赛录像的站内 participant；这些 participant 创建时可能已经创建过 `TournamentUser`，删除时不会回收用户汇总行。
- checkin 读路径只读取缓存，不在未命中时查询 DB 或重建缓存；缓存与 DB 不同步属于写路径维护 bug。
- `TournamentCache.remove_tournament` 移除 `tournament:normal` 中的比赛时，也会从 `tournament:normal:participants` 的所有用户列表中精确移除对应比赛的参赛关系，避免已结束或已取消比赛继续参与 checkin。
- 删除 participant 只监听 `TournamentParticipant.post_delete`；删除 GSC participant 时，多表继承会级联删除父表，参赛关系缓存清理由父类 `post_delete` 的 `remove_participant_cache_on_delete` 统一处理。`post_delete` 中应先捕获 `user_id` 和 `tournament_id`，再在 `transaction.on_commit` 回调中调用 `TournamentCache.remove_participant`。
- 缓存更新和删除应尽量在事务提交后执行；创建 participant 后补录既有录像、创建 `TournamentUser` 是关系/汇总数据维护，不属于缓存失效，按上面的规则立即执行。`TournamentUser` 的创建和 total/best 更新属于数据库数据完整性维护，不适用缓存的 `on_commit` 规则。

当前重构状态：

- `TournamentCache` 已开始封装比赛和参赛关系缓存读写，包括 `get_tournament`、`get_tournament_all`、`get_gsc`、`get_participant_list`、`set_participant_list`、`update_participant`、`remove_participant`、`checkin_arbiter` 和 `checkin_token`，读取结果已改为 dataclass。
- `tournament.services.checkin_with_arbiter` / `checkin_with_token` 负责 checkin 判定，返回命中的比赛列表。
- `checkin_video_before_create` 只在 `VideoModel.pre_save` 创建前阶段运行，此时新录像还没有主键；信号局部暂存命中的比赛列表到 `_checked_in_tournaments`，并设置 `ongoing_tournament=True` 阻止普通个人纪录和排行刷新；`post_save(created=True)` 的 `add_created_video_to_checked_tournaments` 再消费 `_checked_in_tournaments` 写入 `Tournament.videos` 多对多关系。比赛 token 来源直接读取 `ExpandVideoModel.tournament_identifier`，不再通过创建 `VideoModel` 时的临时 token 属性传入。
- EVF 路径在没有参赛缓存时直接跳过 checkin；用户需要先通过 GSC 注册接口显式创建 participant。
- `serialize_normal_participant` 应继续兼容 `arbiter_identifier=None` 的参赛关系，因为 GSC participant 只依赖固定 token。

当前已重新运行 `python -m flake8 tournament` 和 `manage.py test tournament --keepdb`。后端检查通过，测试套件 42 个用例通过。

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

## TODO: 暂不实现的接口

- TODO: `hide_videos_for_tournament(tournament)` 暂非必要。
  - 新上传录像仍由当前单条 `VideoModel` 创建信号路径处理。
  - 如果未来需要补录或批量隐藏比赛录像，再按同样原则设计批处理。
- TODO: `refresh_ongoing_tournament_for_range(start_id, end_id)` 暂非必要。
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

- TODO: 明确比赛取消、状态回滚时应在哪些入口调用 `reveal_videos_for_tournament`。
- TODO: 补充测试：
  - 比赛颁奖后，上万条录像不逐条触发 `VideoModel.save()`。
  - 录像从比赛恢复普通后，队列缓存恢复。
  - 录像从比赛恢复普通后，经典个人纪录和 pluck 纪录刷新。
