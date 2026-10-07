# 后端自定义管理命令

本文档记录当前后端项目中的自定义 Django management commands。命令均在 `back_end/saolei` 目录下执行：

```bash
python manage.py <command>
```

## 本地公开数据快照

### `dangerzone.init_local_test`（独立脚本）

下载和初始化入口分别位于 `dangerzone/download_public_data.py`、`dangerzone/init_local_test.py`。在 `back_end/saolei` 目录使用 `python -m` 启动，后端根目录不再保留同名入口脚本。

仅用于替换本地测试数据，**会清空本地数据库和 `saolei_website` 对应的 Redis 数据库**。此功能不注册为 Django 管理命令，`manage.py` 不提供 `import_public_data`。执行前停止本地后台 worker、定时任务和其他写入；不需要启动 HTTP 服务。要求不存在项目配置的 `.production` 标记、`DEBUG=True`、`E2E_TEST=True`，数据库及 Redis 均为回环地址。即使误开调试选项，存在生产标记仍会拒绝导入。正式导入前检查快照校验和、引用关系和数据库迁移状态。

```bash
# 仅 GET 生产公开 API，每次响应完成后至少等待 1.25 秒；失败后重复执行可续传。
python -m dangerzone.download_public_data
# detailbulk 不可用时，使用已有详情及公开录像列表完成快照：
python -m dangerzone.download_public_data --skip-details
python manage.py migrate
# 读取快照，清库、导入，并创建当天经典周赛。
python -m dangerzone.init_local_test
# 只导入，不创建周赛：
python -m dangerzone.init_local_test --no-weekly
```

默认快照目录是 `back_end/saolei/tmp/public-data`，已由 Git 忽略。下载脚本使用 `--output-dir`，导入脚本使用 `--snapshot-dir` 指定其他目录。已完成的快照不会自动重新下载，获取新快照请换一个目录。

下载通过 `infoupdated` 获取用户 ID，调用 `userprofile/infobulk` 下载用户资料，通过每个用户的 `videolist` 建立公开录像索引，再调用 `video/detailbulk` 下载详情。保留 ID 空洞，不会因空页提前停止。索引后被删除或变成不可见的录像列入 `manifest.json` 的 `unavailable_video_ids`。这不是跨请求一致的数据库备份。TLS 使用 `certifi` 的 CA 包验证，不跳过证书检查；遇到 429 或服务端临时错误会等待重试。

请求串行执行，上一响应完成后至少等待 1.25 秒再发送下一请求，主动控制 `videolist` 在每秒一次以内。`--interval` 可增加间隔，不能低于 1.25 秒；慢请求结束后也不会立即发送下一个请求。

`--skip-details` 不请求 `detailbulk`，已有的详情仍然优先使用，其他录像直接使用 `get_user_videos` 的列表数据；只有列表数据的录像列入 `missing_detail_video_ids`。可空的缺失指标保持 NULL，录像内标识为空字符串。列表里的 `cl`、`ce` 不能直接写入生成列，缺少分项点击数时，相关生成值也为 NULL。生产列表已返回 `right_ce`，列表回退也可以按 `right_ce == 0` 重建 NF 榜；详情缺少该字段或为 NULL 时保留列表值。旧快照缺失该值时保持 NULL，不凭旧模式编码推测。完成的快照不会重新下载，补充新字段或详情请使用新的 `--output-dir` 下载，再通过 `--snapshot-dir` 导入。

导入保留原用户/录像 ID、上传时间和公开属性，旧 NF 模式 `12` 转成 STD `00`，不修改 `right_ce`。批量写入不会触发录像信号，随后重建录像计数、上传额度、扫雷网普通/NF 榜、PB 普通/NF 榜、pluck 纪录缓存和录像状态队列，不创建 pluck 计算任务。

- 管理员：ID `2`，密码 `admin123456`；普通账号：ID `48`，密码 `user123456`。用户名保留生产数据；可通过 `--admin-password` / `--user-password` 指定其他密码。
- 其他用户禁用密码登录，且所有用户中仅 ID `2` 获得本地 `is_staff` 权限；邮箱统一为 `user-{id}@example.invalid`。生产账号不受影响。
- 这两个公开详情 API 不提供原密码、邮箱、录像文件、头像文件、标识绑定和比赛关联；不会推测这些数据。录像可以用于列表和排行测试，但不能在本地播放或重新解析。录像计数只能基于本次导入的公开录像计算，无法排除缺失比赛关联的已公开比赛录像。
- `is_lucky` 当前未由这两个详情 API 提供，导入保留模型默认值。已有 `pluck` 从公开录像列表补齐，缺失时保持 NULL，不重新解析录像。
- 再次初始化会丢弃之前的本地数据；应使用独立的本地数据库及 Redis 数据库。不要对生产配置运行这些命令。

## 缓存重建

### `rebuild_speed_ranks`

位置：`speedranking/management/commands/rebuild_speed_ranks.py`

从 `VideoModel` 按玩家分段重建竞速排行榜。`--ranking-name` 可选 `saolei` 或 `saolei_nf`，省略则重建两者；`--batch-size` 默认 1000，必须为正数。

```bash
python manage.py rebuild_speed_ranks
python manage.py rebuild_speed_ranks --ranking-name saolei_nf --batch-size 1000
```

执行前暂停录像上传、修改、删除、标识绑定/解绑及比赛公开等写入。命令先构建临时榜，成功后原子发布单个大榜，最后清理临时缓存。构建失败保留该大榜的原缓存；两个大榜依次替换。排行 API 不自动回源，因此首次部署及缓存丢失后都需要执行此命令。重建不恢复旧新闻。

从旧的“微秒时间戳 + 玩家 id” member 升级为纯玩家 id、分钟级合成 score 时，应暂停相关读写，以新代码执行不带 `--ranking-name` 的重建命令，两个大榜都完成后再恢复服务。超出编码范围的单项或总值仍保存在个人纪录 hash，仅不写入对应 zset；总榜独立判断，不修改录像数据库和个人最佳选取规则。

### `rebuild_pb_ranks`

位置：`speedranking/management/commands/rebuild_pb_ranks.py`

从录像数据库重建 PB 普通/NF 榜、用户 rank hash 和小榜人数 hash。`--batch-size` 默认 100，必须为正数；按玩家 id 分段，每批输出累计用户数和最后玩家 id，最后逐小榜刷新排名并同步人数。清空 PB 命名空间时也会删除旧人数 hash；重建后未出现的小榜按 0 人处理。

```bash
python manage.py rebuild_pb_ranks --batch-size 100
```

首次部署及 PB 缓存丢失后需要手动执行，API 不回源。执行前暂停 PB 相关读写，包括上传、审核、绑定/解绑、删除及比赛公开。命令直接清空 PB 命名空间后重建，不使用临时榜或原子发布；失败会记录日志并中断，可能留下部分缓存，排除错误后重新运行。录像数据库和扫雷网缓存不受影响。`rebuild_speed_ranks` 仍仅重建扫雷网规则。

本地快照初始化 `python -m dangerzone.init_local_test` 已在扫雷网重建后自动调用 PB 重建，使用 `--no-weekly` 时也会执行，无需另外运行上述命令。

### `rebuild_tournament_cache`

位置：`tournament/management/commands/rebuild_tournament_cache.py`

用途：重建比赛 Redis 缓存，包括当前 `NORMAL` 状态的比赛和这些比赛的参赛关系。

主要行为：

- 清空 `tournament:normal` 和 `tournament:normal:participants`。
- 读取 `NORMAL` 状态的 `GSCTournament` 和 `WeeklyTournament`。
- 将比赛基础信息写入 `tournament:normal`。
- 将当前 `NORMAL` 比赛的参赛关系按用户分组写入 `tournament:normal:participants`。

常用命令：

```bash
python manage.py rebuild_tournament_cache
```

### `rebuild_tournament_user_cache`

位置：`tournament/management/commands/rebuild_tournament_user_cache.py`

用途：重建 `TournamentUser` 的 Redis 排行缓存。

参数：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--batch-size` | `1000` | 每批处理的缓存行数 |

常用命令：

```bash
python manage.py rebuild_tournament_user_cache
python manage.py rebuild_tournament_user_cache --batch-size 500
```

### `rebuild_custom_pluck_cache`

位置：`customranking/management/commands/rebuild_custom_pluck_cache.py`

用途：重建自定义 pLuck 排行的 Redis 缓存。

参数：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--level` | 无 | 只重建指定自定义级别；省略则重建全部配置 |
| `--batch-size` | `1000` | 每批写入 Redis 的纪录数量 |

当前 `--level` 的合法值来自 `CUSTOM_PLUCK_CONFIGS`：

| 参数值 | 配置 |
| --- | --- |
| `c8_8_40` | 8x8 40 雷 |
| `c16_16_100` | 16x16 100 雷 |
| `c16_30_150` | 16x30 150 雷 |
| `c24_30_200` | 24x30 200 雷 |

常用命令：

```bash
python manage.py rebuild_custom_pluck_cache
python manage.py rebuild_custom_pluck_cache --level c16_30_150
python manage.py rebuild_custom_pluck_cache --batch-size 500
```

## 数据刷新

### `refresh_videos`

位置：`videomanager/management/commands/refresh_videos.py`

用途：替代旧 `refresh_stnb` 的录像重解析入口，对指定 ID 范围内的 `VideoModel` 实例逐条调用 `videomanager.view_utils.refresh_video`，默认刷新全部录像。

- 按主键顺序遍历，不限制状态、模式、级别或比赛标记。
- 使用 `iterator()` 遍历录像 ID，避免 QuerySet 缓存所有实例；写入仍逐条执行，不使用 `update()` 或 `bulk_update()`。
- 每条录像使用独立的 `transaction.atomic()`，通过 `select_for_update()` 加锁并重新读取该条主表记录后执行刷新，不连带锁住查询关联的用户等记录。解析与主表、扩展表保存均在该事务内；完成或失败后释放锁，不对全部录像使用一个长事务。其他事务修改或删除同一主表记录时会等待，因此耗时解析期间仍可能阻塞该条录像的写入。
- 沿用 `refresh_video` 的差异保存逻辑，通过 `save(update_fields=...)` 触发信号；没有变化的字段不会强制保存。
- 已知的录像解析异常会包装为 `VideoParseError`，报告录像 ID 并跳过，继续刷新后续录像；结束时汇总成功和跳过数量。
- 数据库、文件读写、保存或信号接收器等其他错误会停止命令；当前条的数据库写入回滚，此前完成的刷新不会整体回滚。不会把刷新全过程中的 `ValueError` 等异常都视为解析错误。事务不回滚已经直接写入 Redis 的副作用。
- 此命令不是无条件的排行榜或缓存全量重建。刷新模式等字段后如需重算录像计数，仍使用 `refresh_video_counts`。
- 每处理 `step` 条录像输出并立即刷新进度，包括已处理数量、成功数量、跳过数量和当前录像 ID。解析失败也计入已处理数量；不足 `step` 的剩余部分在最终汇总中体现。

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--start` | `0` | 起始录像 ID，包含，必须非负 |
| `--end` | 不限制 | 结束录像 ID，不包含，不能小于 `start` |
| `--step` | `100` | 每处理多少条录像输出一次进度，必须为正整数 |

区间采用 `[start, end)`，按录像 ID 筛选而非列表偏移；ID 存在空缺时，`step` 仍按实际处理条数计数。可以仅指定一个边界，或使用相邻区间连续分段刷新。

```bash
python manage.py refresh_videos
python manage.py refresh_videos --start 10000 --end 20000 --step 50
python manage.py refresh_videos --start 20000 --end 30000 --step 50
```

### `refresh_video_counts`

位置：`msuser/management/commands/refresh_video_counts.py`

用途：刷新全部 `UserMS` 的录像总数，以及各级别、模式的录像计数。

- 排除 `ongoing_tournament=True` 的录像，以及通过 `Tournament.videos` 关联的所有比赛录像（包括已结束比赛）。
- 普通录像不按审核状态筛选；没有普通录像的用户计数归零。
- 按用户分批聚合并写入，不修改 `video_num_limit` 或个人纪录，也不更新 Redis。
- 可重复执行。为避免与上传、删除并发造成计数覆盖，执行时应暂停录像写入。

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--batch-size` | `1000` | 每批处理的用户数量，必须为正整数 |

```bash
python manage.py refresh_video_counts
python manage.py refresh_video_counts --batch-size 500
```

### `refresh_tournament_scores`

位置：`tournament/management/commands/refresh_tournament_scores.py`

用途：同步重算指定已颁奖比赛的成绩、排名、积分和参赛用户的历史最佳成绩，无需后台 worker。支持 GSC 和经典周赛。

- 参数为比赛 ID，不是 GSC 届数或周数；只接受已颁奖、有结束时间的 GSC 或经典周赛。
- 从关联的有效录像重新计算成绩，再刷新 `rank` 和 `rank_score`。缺少的成绩恢复默认值，不保留已失效录像的旧成绩。
- 按新旧 `rank_score` 的差额修正历史积分总量，不重复累计。当前积分加入从该届结束时间衰减到 `last_updated` 的差额；若该届结束得更晚，则先将原当前积分衰减到该届结束时间。
- `last_updated` 表示最后结束的比赛时间，不因重算历史比赛而回退。积分及个人历史最佳成绩的 Redis 缓存同步刷新；历史最佳成绩支持变好和变差。
- 不删除参赛者、不修改比赛状态、不公开录像、不重新解析录像文件。
- 执行期间应避免同时修改该届的录像或参赛者，并暂停涉及这些用户的积分结算。该届的数据库写入在一个事务内，中途失败会回滚，可在排除故障后重跑；Redis 已写入的内容不会随数据库回滚，失败后需重跑以恢复缓存一致性。

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `tournament_id` | 必填 | 比赛 ID，不是 GSC 届数或周数 |
| `--batch-size` | `1000` | 批量写入大小，必须为正整数 |

```bash
python manage.py refresh_tournament_scores 123
python manage.py refresh_tournament_scores 123 --batch-size 500
```

### `refresh_tournament_user_stats`

位置：`tournament/management/commands/refresh_tournament_user_stats.py`

用途：刷新 `TournamentUser` 的历史 total 和 best 字段，不修改实时 `score_current`。

主要行为：

- 根据已有 `TournamentUser` 和已颁奖比赛的参赛关系补齐缺失的 `TournamentUser`。
- 刷新比赛积分历史总分。
- 刷新金羊杯和打卡赛历史最好成绩。
- 将更新后的历史字段同步到 Redis 缓存。

参数：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--batch-size` | `1000` | 批量创建、批量更新和缓存写入的批大小 |

常用命令：

```bash
python manage.py refresh_tournament_user_stats
python manage.py refresh_tournament_user_stats --batch-size 500
```

## 缓存清理

### `delete_legacy_speedranking_cache`

位置：`common/management/commands/delete_legacy_speedranking_cache.py`

用途：竞速排行榜重构第一步中，清理旧排行榜和新闻的 Redis key。应在停用旧功能的写入逻辑后执行，否则旧代码会重新生成缓存。

- 清理`player_{stat}_{mode}_{用户ID}`和`player_{stat}_{mode}_ids`：指标限于`timems`、`bvs`、`stnb`、`ioe`、`path`，模式限于`std`、`nf`、`ng`、`dg`。
- 清理`news_queue`，不依赖该key是list还是zset。
- 保留自定义pluck排行、比赛缓存、录像队列及其他Redis数据，不修改数据库。
- 使用`saolei_website` Redis连接，通过`SCAN`遍历，每批最多1000个key，用`UNLINK`删除。可重复执行。

```bash
python manage.py delete_legacy_speedranking_cache --dry-run
python manage.py delete_legacy_speedranking_cache
```

`--dry-run`仅列出匹配的key并统计数量，不删除数据。

### `delete_newest_queue`

位置：`videomanager/management/commands/delete_newest_queue.py`

用途：调用 `videomanager.services.delete_newest_queue`，清理 Redis 最新录像队列。

队列不超过 100 条时不处理；超过 100 条时删除所有超过 7 天的记录，因此清理后可能少于 100 条。该逻辑也由 `runapscheduler` 每天 01:08 调用。

常用命令：

```bash
python manage.py delete_newest_queue
```

## 后台任务与定时任务

### `db_worker_robust`

位置：`common/management/commands/db_worker_robust.py`

用途：安全启动 `django-tasks-db` worker。启动前会处理孤儿 `RUNNING` 任务，并通过 pidfile 防止重复 worker。

主要行为：

- 使用 pidfile 防止重复启动。
- 检测当前是否已有 `db_worker` 或 `db_worker_robust` 进程。
- 若没有正在运行的 worker，则将遗留的 `RUNNING` 任务标记为 `FAILED`。
- 调用 Django 内置的 `db_worker` 开始处理任务。

参数：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--queue-name` | 默认任务队列 | 要处理的队列；多个队列用逗号分隔，`*` 表示全部 |
| `--interval` | `2` | worker 轮询间隔，单位秒 |
| `--backend` | 默认任务后端 | 使用的 task backend |
| `--batch` | `False` | 传递给 `db_worker` 的批处理模式 |
| `--no-startup-delay` | `False` | 关闭 `db_worker` 的启动延迟 |
| `--max-tasks` | 无 | 最多处理的任务数 |
| `--worker-id` | 自动生成 | 覆盖自动生成的 worker id |
| `--pidfile` | `logs/db_worker_robust.pid` | 用于防止重复启动的 pidfile 路径 |

常用命令：

```bash
python manage.py db_worker_robust
python manage.py db_worker_robust --queue-name default --interval 2
```

### `runapscheduler`

位置：`common/management/commands/runapscheduler.py`

用途：启动所有 APScheduler 定时任务。当前 APScheduler 已合并为 `common` APP 中的单一常驻进程，避免分别启动监控、用户和录像相关的三个 Django 进程。

任务注册位置：`common/apscheduler.py`

定时任务：

| 任务 | 频率 | 说明 |
| --- | --- | --- |
| `refresh_state_always` | 每 5 秒 | 采集网络 IO 速度和 CPU 使用率，并写入 Redis |
| `delete_old_job_executions` | 每周一 00:03 | 清理旧的 APScheduler job execution 记录 |
| `delete_newest_queue` | 每天 01:08 | 队列超过 100 条时删除超过 7 天的记录 |
| `delete_freezed_video` | 每天 01:28 | 删除 7 天以前冻结状态的录像 |
| `delete_overdue_emailverifyrecord` | 每周一 01:03 | 清理 1 小时以前的邮箱验证码 |
| `delete_overdue_captcha` | 每周一 01:05 | 清理过期图形验证码 |

参数：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--pidfile` | `logs/apscheduler.pid` | 用于防止重复启动 APScheduler 进程的 pidfile 路径 |

常用命令：

```bash
python manage.py runapscheduler
python manage.py runapscheduler --pidfile logs/apscheduler.pid
```

生产启动：

- `start.sh` 会在数据库迁移完成后启动该命令，日志写入 `logs/apscheduler.log`。
- `START_APSCHEDULER=0` 可跳过启动 APScheduler。
- `APSCHEDULER_START_DELAY` 控制启动延迟，默认 `10` 秒。
- `APSCHEDULER_NICE` 控制进程 nice 值，默认 `10`。

::: warning
生产环境只应运行一个 APScheduler 进程。旧的 `runapschedulermonitor`、`runapscheduleruserprofile` 和 `runapschedulervideomanager` 命令已合并到 `runapscheduler`，不应再单独启动。
:::

## 维护建议

- 新增管理命令后，应同步更新本文档。
- 改动缓存结构后，应检查对应的重建命令是否仍能从数据库恢复 Redis 状态。
- 全量刷新类命令应在低流量时执行，并在执行前确认是否需要备份。
- 定时任务命令是常驻进程，生产环境应由进程管理工具启动和守护。
