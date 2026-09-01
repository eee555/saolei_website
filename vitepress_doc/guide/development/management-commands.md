# 后端自定义管理命令

本文档记录当前后端项目中的自定义 Django management commands。命令均在 `back_end/saolei` 目录下执行：

```bash
python manage.py <command>
```

## 缓存重建

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

### `refresh_stnb`

位置：`videomanager/management/commands/refresh_stnb.py`

用途：根据录像文件全量更新官方录像数据，并重建由 `iqg` 派生的 `stnb` 个人纪录及相关排行缓存。

主要流程：

1. 重解析所有 `OFFICIAL` 录像文件，刷新录像基础数据。
2. 重算有官方录像用户的个人纪录和 Redis 排行缓存。
3. 清空 `news_queue`，避免历史 PB 重新计算后污染首页动态。

参数：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--video-delay` | `0.05` | 每批录像间延时秒数 |
| `--user-delay` | `0.2` | 每个用户间延时秒数 |
| `--yes` | `False` | 跳过确认提示，直接执行 |

常用命令：

```bash
python manage.py refresh_stnb
python manage.py refresh_stnb --yes
python manage.py refresh_stnb --video-delay 0 --user-delay 0 --yes
```

::: warning
这是侵入性较强的全量刷新命令。执行前建议备份相关数据库表和 Redis，执行期间不应有用户上传录像。
:::

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

### `runapschedulervideomanager`

位置：`videomanager/management/commands/runapschedulervideomanager.py`

用途：启动 `videomanager` 相关 APScheduler 定时任务。

定时任务：

| 任务 | 频率 | 说明 |
| --- | --- | --- |
| `delete_newest_queue` | 每天 01:08 | 清理 Redis 最新录像队列，保留最近 7 天或至少 100 条 |
| `delete_freezed_video` | 每天 01:28 | 删除 7 天以前冻结状态的录像 |
| `delete_old_job_executions` | 每周一 00:03 | 清理旧的 APScheduler job execution 记录 |

常用命令：

```bash
python manage.py runapschedulervideomanager
```

### `runapschedulermonitor`

位置：`monitor/management/commands/runapschedulermonitor.py`

用途：启动服务器监控相关 APScheduler 定时任务。

定时任务：

| 任务 | 频率 | 说明 |
| --- | --- | --- |
| `refresh_state_always` | 每 5 秒 | 采集网络 IO 速度和 CPU 使用率，并写入 Redis |
| `delete_old_job_executions` | 每周一 00:03 | 清理旧的 APScheduler job execution 记录 |

常用命令：

```bash
python manage.py runapschedulermonitor
```

### `runapscheduleruserprofile`

位置：`userprofile/management/commands/runapscheduleruserprofile.py`

用途：启动用户相关 APScheduler 定时任务。

定时任务：

| 任务 | 频率 | 说明 |
| --- | --- | --- |
| `delete_overdue_emailverifyrecord` | 每周一 01:03 | 清理 1 小时以前的邮箱验证码 |
| `delete_overdue_captcha` | 每周一 01:05 | 清理过期图形验证码 |
| `delete_old_job_executions` | 每周一 00:03 | 清理旧的 APScheduler job execution 记录 |

常用命令：

```bash
python manage.py runapscheduleruserprofile
```

## 维护建议

- 新增管理命令后，应同步更新本文档。
- 改动缓存结构后，应检查对应的重建命令是否仍能从数据库恢复 Redis 状态。
- 全量刷新类命令应在低流量时执行，并在执行前确认是否需要备份。
- 定时任务命令是常驻进程，生产环境应由进程管理工具启动和守护。
