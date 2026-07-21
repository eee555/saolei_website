# videomanager 事件流说明

本文档记录 `VideoModel` 创建、修改后需要触发的逻辑，以及会互动的 app。当前代码仍处在解耦过程中，后续修改事件逻辑时应先更新本文档。

## 核心模型

- `VideoModel`：录像主表，保存玩家、文件、审核状态、级别、模式、成绩、`pluck`、比赛标记等信息。
- `ExpandVideoModel`：录像扩展信息，目前主要保存录像内标识 `identifier`。

`VideoModel` 是多个 app 的事实事件源。任何保存 `VideoModel` 的代码都应尽量使用 `save(update_fields=[...])`，让信号接收器能判断本次修改的影响范围。

## 创建录像

主要入口：

- `common.utils.new_video_by_file`
- `VideoModel.create_from_parser`
- `accountlink.services.saolei_video_import_one`
- 管理命令或测试中直接 `VideoModel.objects.create`

创建前通常需要完成：

- `utils.parser.MSVideoParser` 解析录像文件，得到基础字段、扩展字段、状态、标识、比赛 token、`pluck`。
- `identifier` 检查标识安全性和归属。如果录像本身合法但标识不属于用户，状态应降为 `IDENTIFIER`。
- 文件重复检查。

创建时需要触发：

- `tournament`：`pre_save(VideoModel)` 根据 `_tournament_identifiers` 执行比赛 check-in，并可能设置 `ongoing_tournament=True`；`post_save(VideoModel)` 在录像获得主键后写入比赛的 `videos` 多对多关系。
- `videomanager`：创建后需要进入对应审核队列或最新队列；队列副作用应由 `videomanager.signals` 统一处理。
- `msuser`：如果录像满足经典排行条件，`post_save(VideoModel)` 会在创建时尝试更新经典个人纪录。
- `customranking`：自定义 pluck 排行需要录像满足 `OFFICIAL`、非比赛、合法自定义配置、`pluck is not None`。当前通过 `VideoModel` 保存后的信号维护 `CustomPluckRecord`。
- `utils.parser.MSVideoParser`：标准三等级和当前支持的自定义 `pluck` 场景都会在解析时前台计算，保存 `VideoModel` 后触发 `customranking`。
- `videomanager.tasks`：`task_video_pluck` 入口保留，供未来重新需要后台计算时复用。

## 修改录像字段

### `state`

影响：

- `videomanager`：录像应从旧状态队列移除，并加入新状态队列。
- `msuser`：如果录像从可入榜变为不可入榜，或反过来，需要更新或重建个人纪录。
- `customranking`：如果自定义 pluck 录像变为 `OFFICIAL`，可尝试加入排行；如果变为不可排行状态，需要移除该录像影响。
- `identifier`：标识绑定/解绑会间接修改录像 `state`。

推荐写法：

```python
video.state = MS_TextChoices.State.OFFICIAL
video.save(update_fields=['state'])
```

不推荐在业务代码中直接维护多个 app 的副作用。

### `ongoing_tournament`

影响：

- `videomanager`：比赛录像不应进入缓存队列。
- `msuser`：比赛录像不进入纪录。
- `customranking`：比赛录像不进入纪录。
- `tournament`：该字段由比赛 check-in 逻辑设置，表示录像属于进行中的比赛。比赛结束后，应将 `ongoing_tournament` 设置为 `False`。

推荐写法：

```python
video.ongoing_tournament = True
video.save(update_fields=['ongoing_tournament'])
```

### `pluck`

影响：

- `customranking`：保存 `pluck` 后，如果录像满足 density 排行条件，应刷新对应玩家的 `CustomPluckRecord` 和 Redis 前排缓存。
- `utils.parser.MSVideoParser`：普通三等级和当前支持的自定义录像都会在解析时直接计算 `pluck`。

推荐写法：

```python
video.pluck = pluck
video.save(update_fields=['pluck'])
```

### 经典排行字段

严格依赖：
- `msuser`：timems纪录依赖`timems`，bvs纪录依赖`timems`和`bv`（虽然有`bvs`但是其为`GeneratedField`），stnb纪录依赖`iqg`（同一`level`内按`iqg`排序，最终值由`VideoModel.stnb`属性乘以等级系数得到），ioe纪录依赖`left`、`right`、`double`和`bv`（同样是`GeneratedField`），path纪录依赖`path`。
- `customranking`：pluck纪录依赖`pluck`。

Tie-Breaker依赖：timems相同时比较`upload_time`（越小越好），其他纪录相同时依次比较`timems`（越小越好）和`upload_time`（越小越好）。

排行分类依赖：`level`、`mode`
- `msuser`：仅接受`level`为初级、中级、高级，`mode`为标准（对应STD）、盲扫（对应NF）、无猜（对应JSW）、递归（对应BZD），共计12种组合。

正常业务中这些字段创建后不应频繁修改。若数据迁移需要修改，应优先使用批处理刷新接口重建相关排行，而不是依赖逐条信号完成所有修复。

### 文件和解析字段

`refresh_video(video)` 会重新解析文件并刷新所有文件包含的数据。

如果重新解析后 `IDENTIFIER` 录像的标识已经属于玩家，可将状态改为 `OFFICIAL`，并通过状态保存触发后续事件。

## 互动 app

### `identifier`

职责：

- 维护标识文本是否安全、是否绑定到某个 `UserMS`。
- 当标识绑定、解绑、转移、删除或变为不安全时，修改相关录像的 `state`。

互动方式：

- `identifier.signals` 查询相关 `VideoModel`，将匹配录像在 `IDENTIFIER` 和 `OFFICIAL` 之间切换。
- 状态切换后由 `videomanager`、`msuser`、`customranking` 的 `VideoModel` 信号继续处理副作用。

### `tournament`

职责：

- 创建录像前识别比赛 token 或 Arbiter 标识。
- 对进行中比赛设置 `video.ongoing_tournament=True`。
- 创建后把录像加入比赛的 `videos` 多对多关系。
- 比赛结束后为比赛录像设置 `video.ongoing_tournament=False`。

互动方式：

- `VideoModel.create_from_parser` 在实例上暂存 `_tournament_identifiers`。
- `tournament.signals` 在 `pre_save` / `post_save` 中完成 check-in。

### `msuser`

职责：

- 维护经典三等级个人纪录和相关 Redis 个人纪录缓存。

互动方式：

- `videomanager.signals` 在 `pre_save(VideoModel)` 捕获 `_old_values`，`msuser.signals` 在 `post_save(VideoModel)` 读取它。
- `msuser.signals` 根据旧分类和新分类决定处理方式：分类不变时按字段变好/变差做局部更新，分类变化时重建旧分类并尝试加入新分类。
- 经典排行只接受三等级 `b/i/e`，以及 `STD/NF/JSW/BZD` 四类录像模式。
- `stnb` 由 `VideoModel.iqg` 和等级系数派生，不再依赖 `ExpandVideoModel`。
### `customranking`

职责：

- 维护pluck自定义排行榜。
- 每个玩家、每个支持的自定义配置只保留一条最佳 `CustomPluckRecord`。
- Redis 缓存保存排行榜前段。

互动方式：

- `customranking.signals` 监听 `VideoModel` 的 `state`、`ongoing_tournament`、`pluck`、`timems`、`upload_time`。
- `CustomPluckRecord` 保存或删除后，同步更新 Redis 排行缓存。

### `common`

职责：

- 提供上传入口，做文件、用户、标识和重复录像检查。
- 调用 `VideoModel.create_from_parser` 创建录像。
- 创建后触发必要的保存和队列更新。

当前上传链路中仍有显式调用 `video.update_redis()`，但它不应再直接维护队列；队列写入和移除由 `videomanager.signals` 处理。

### `accountlink`

职责：

- 从外部站点导入录像。
- 复用 parser 和 `VideoModel.create_from_parser`。
- 导入后可能修改 `upload_time`，并触发同样的录像事件链。

## TODO

- `VideoModel.update_redis()` 已经不再维护 Redis 队列，且 `pluck` 调度和录像数量统计职责也已移出；名称和剩余职责都已经过时。
  - 当前实际职责只剩按录像状态写上传日志。
  - 上传日志应迁移到 `videomanager.signals`，和队列事件同属录像状态/创建事件的本 app 副作用。
  - 完成日志迁移后，应删除 `update_redis()`，上传、导入等入口不再需要显式调用它。
- 录像数量统计已迁移到 `msuser.signals`。
  - 创建录像会增加总数统计；删除录像会减少总数统计。
  - 经典级别和模式会同步维护对应子计数；自定义或其他模式只影响总数。
  - `video_num_limit` 只会在符合条件的高级标准官方录像保存后提升，删除录像不会回退上限。
  - 后续若要处理状态回退、模式/级别变化，应先明确统计口径，再扩展 `msuser.signals`。
- `videomanager.signals` 是 `_old_values` 的统一来源，新增依赖旧值的 app 时应先扩展 `CAPTURE_FIELDS`。
  - 当前覆盖队列、经典纪录、custom pluck 排行所需字段。
  - 如果未来新增依赖 `file_size`、`end_time`、`cell*`、`flag/op/isl` 等字段的副作用，需要同步补充。
- 批量修改仍不能依赖普通 `save()` 信号。
  - `identifier` 当前逐条保存录像状态，能触发事件流，但大批量时可能较慢。
  - 比赛结束批量设置 `ongoing_tournament=False`、数据迁移批量修改 `state/level/mode/player/timems` 时，需要专门批处理逻辑或 `django-bulk-tracker`，否则排行和队列不会自动保持一致。
- `update_fields` 仍是信号正确判断影响范围的关键。
  - 不带 `update_fields` 的保存会让接收器按更宽的字段集合工作。
  - 后续可以用 lint 或测试约束重要路径的 `save(update_fields=[...])` 写法。
- `pluck` 计算分工需要保持清晰。
  - 普通三等级录像在 parser 中即时计算。
  - 当前支持的自定义录像也在 parser 中前台即时计算，并通过保存 `pluck` 触发 `customranking`。
  - `task_video_pluck` 仍保留为后台入口；未来如果重新出现耗时过长的场景，可切回任务队列。
  - 如果未来增加新的自定义配置或更昂贵的指标，应先评估是否需要进入后台任务。
- `refresh_stnb` 管理命令名称已经偏旧。
  - 当前命令实际会重解析所有官方录像文件，刷新基础派生字段，并重建经典个人纪录与相关 Redis 缓存。
  - 该命令侵入性较强，执行期间不应有用户上传录像；后续可以考虑改名为更通用的 `refresh_video_records` 或拆分为更小的批处理命令。
- `iqg` 使用数据库 `GeneratedField` 和 `Power` 表达式。
  - 本地测试库已经覆盖基本创建和查询路径。
  - 生产部署前仍需要在同版本数据库环境做迁移预演，确认生成列表达式兼容。

## 修改限制
`customranking`是新增app，可任意修改，无需担心迁移。其他app的迁移需要让django makemigrations能自动完成。


# stnb 支持说明

## 背景

`stnb` 与 `iqg` 成正比，比例系数只由标准三等级决定：

- Beginner: `stnb = 36 * iqg`
- Intermediate: `stnb = 162 * iqg`
- Expert: `stnb = 435 * iqg`

自定义级别没有 `stnb` 定义，因此 `stnb` 个人纪录仍然只适用于经典三等级。

`iqg = bv / (timems / 1000) ^ 1.7` 已作为 `VideoModel` 的 `GeneratedField` 保存，`ExpandVideoModel.stnb` 已删除。`stnb` 纪录由 `VideoModel.iqg` 派生；因此 `stnb` 与 `bvs`、`ioe` 一样属于 `VideoModel` 基础字段变化后的派生指标，不再监听 `ExpandVideoModel` 的保存事件。
