# WOM 公开成绩与累计统计

后端已采用 [wom-api v0.1.0](https://github.com/putianyi889/wom-api/releases/tag/v0.1.0) 替换玩家资料 HTML 抓取，源码提交为 `823c3b0c9c7f6477fafd3767a5ad037320cd48ee`。记录日期：2026-10-13。

当前保留原有成绩字段，新增 22 个公开成绩与累计统计字段。按用户要求删除变动频繁的库存：`honour`、`minecoin`、`gem`、`coin`、`arena_ticket`、`equipment`、`part`。不收录用户名、国家、物品明细、装备配置或完整原始响应。

## 读取和持久化

调用链为 `accountlink/services.py::update_account` → `update_wom_account` → `wom/client.py::fetch_wom_profile` → `WomClient.get_user_detail_data`。读取使用匿名会话，不需要用户 WOM session；公开资料不能证明账号归属，原有人工账号验证流程继续使用。

客户端在同一异步函数内创建和释放，五秒截止时间包括授权、连接、发送排队和响应。同步服务通过 Django 已有的 `asgiref.sync.async_to_sync` 调用；没有新增独立服务或自建 WebSocket 协议。使用库支持的 `system-certs` extra 和 `truststore.SSLContext` 读取系统信任库，HTTP 与 WebSocket 都保持 TLS 证书验证，不修改全局 SSL 配置。

`wom/utils.py::normalize_wom_profile` 先验证玩家 ID、整数统计和成绩结构，再生成更新字段；全部转换完成后才保存模型，并更新 `update_time`。超时映射为 `import/timeout`，连接和授权等库错误映射为 `import/requestexception`，数据结构或身份错误映射为 `import/indexerror`。失败保留已有资料，日志仅包含玩家 ID 和错误类型，不记录授权值。

`AccountWoMOut` 继续由 Ninja 的 `create_schema` 从模型生成。前端数据类型和 `CardWoM.vue` 已同步调整，新增数据未刷新时展示占位符，时长复用 `formatSecondsAsHMS`。

## 保留字段的转换

`stat` 表示全历史 `response['userStat']`，不混入 `seasonUserStat`。

| 本站字段 | WOM 数据及转换 |
| --- | --- |
| `trophy` | `stat.score` |
| `experience` | `stat.exp` |
| `arena_point` / `max_difficulty` / `win` | `stat.arenaPoints` / `stat.diff` / `stat.winsAll` |
| `last_season` | 当前月赛季 ID 转编号：`id - 24192 + 1`；0 为无记录，低于 10000 的旧编号保留，未知编码报错 |
| `b_t_ms` / `i_t_ms` / `e_t_ms` | `timeResults['1'/'2'/'3'].duration`，已是毫秒 |
| `b_ioe` / `i_ioe` / `e_ioe` | `effResults['1'/'2'/'3'].eff100`；保留原整数百分比精度：`((eff100 + 50) // 100) / 100` |
| `b_mastery` / `i_mastery` / `e_mastery` | `stat.mastery1` / `mastery2` / `mastery3` |
| `b_winstreak` / `i_winstreak` / `e_winstreak` | `stat.ws1` / `ws2` / `ws3` |

## 新增字段

| 本站字段 | WOM 数据及语义 |
| --- | --- |
| `b_endurance_ms` / `i_endurance_ms` / `e_endurance_ms` | `86400000 - stat.end1/end2/end3`，存为耐力用时毫秒；原值 0 或 null 时存 86400000；字段默认值为 86400000，不允许 null |
| `b_ng_t_ms` / `i_ng_t_ms` / `e_ng_t_ms` | `timeResults['11'/'12'/'13'].duration`，初/中/高级无猜 PB，单位毫秒 |
| `b_win` / `i_win` / `e_win` | `stat.wins1` / `wins2` / `wins3`，标准各难度累计胜场 |
| `b_ng_win` / `i_ng_win` / `e_ng_win` | `stat.wins11` / `wins12` / `wins13`，无猜各难度累计胜场 |
| `experience_total` | `stat.expAll`，累计获得经验，区别于当前经验 `exp` |
| `minecoin_total` | `stat.coinsAll`，累计获得雷币，区别于库存 `coins` |
| `gem_total` | `stat.gemsAll`，累计获得宝石 |
| `arena_coin_total` | `stat.arenaCoinsAll`，累计获得竞技场币 |
| `game_count` | `stat.games`，公开游戏局数 |
| `win_nf` | `stat.winsNf`，累计无旗胜场；无旗（NF）与无猜（NG）不是同一种模式 |
| `play_time_ms` | `stat.timeAll`，累计游戏用时毫秒 |
| `arena_play_time_ms` | `stat.arenaDuration`，累计竞技场用时毫秒 |
| `bbbv_total` | `stat.bbbvAll`，累计 3BV |
| `season_count` | `stat.seasons`，参与赛季数 |

字段类型按业务数量级选择：仅累计游戏和竞技场毫秒用时使用 nullable `PositiveBigIntegerField`；累计 3BV、经验、金币、其他资源、局数及胜场使用 nullable `PositiveIntegerField`；每月一个赛季的参与赛季数使用 nullable `PositiveSmallIntegerField`。转换时按当前 MySQL 的字段范围校验：普通计数不超过 `2**32 - 1`，赛季数不超过 `2**16 - 1`，累计用时不超过 `2**63 - 1`；越界响应报解析错误，不覆盖已有资料。

类型选择依据用户提供的业务约束：平均 3BV/s 达不到 10；累计经验高于 3BV 但同量级，累计金币与 3BV 同量级，其他资源至少低一个数量级；累计局数小于 3BV，累计胜场至少低四个二进制位。按 10 3BV/s 连续计算，32 位无符号 3BV 容量约对应 13.6 年，作为数量级估算而非严格终身上限。毫秒累计用时的 32 位容量仅约 49.7 天，因此保留 64 位。

三个耐力用时字段使用 `default=86400000, null=False`，无耐力成绩时存为 24 小时，前端显示 `24:00:00`。其余新字段在旧记录中初始为 null，首次成功刷新后填入；有效计数 0 保留 0，缺少某难度时间或效率 PB 时存 null。

如果整个 `userStat` 为 null，仅在 `noUserStatExp` 是有效非负整数时更新经验，其他已存字段保留；负一表示不可读取。顶层记录表被省略时保留对应旧值，明确返回空记录表时清除该表的 PB。未知或错误类型报错，避免误将隐藏或异常资料清零。

本次玩家 1783173 的公开样本中，耐力用时为 582000 / 2591000 / 13888000 毫秒，无猜 PB 为 1282 / 16720 / 48877 毫秒；累计获得经验为 21163169，累计雷币为 3901062，累计用时为 2808349910 毫秒。冻结样本 `test/public_profile.json` 只保留测试使用的字段和 ID，没有用户名、国家、库存或授权值。在线成绩随时间变化，不应使用实时资料的固定值断言。

WOM 的映射、客户端和数据库/API 测试统一放在 `test/tests.py`，fixture 同目录存放。运行：`python manage.py test accountlink.wom.test --keepdb`；Django 的常规测试发现也会包含这些测试。

## 迁移和验证

迁移 `accountlink/migrations/0010_wom_public_statistics.py` 由 Django `makemigrations accountlink --name wom_public_statistics` 自动生成。它删除 7 个库存列、添加 22 个统计列，不用当前库存推算累计资源。后续 `0011_wom_counter_sizes.py` 用于收紧累计计数类型，`0012_wom_endurance_defaults.py` 将三个耐力字段设为非空并把已有空值填为 86400000；均由 Django 自动生成。保留已存在的迁移，兼容已经应用它们的数据库。项目忽略新迁移文件，提交时需要使用 `git add -f` 显式收录这三份迁移。

`requirements.txt` 使用 `wom-api[system-certs]==0.1.0`，通过 pip 的 `--find-links wheels` 从本地目录发现发布包。`requirements-wheels.txt` 单独固定 [GitHub 发布包](https://github.com/putianyi889/wom-api/releases/tag/v0.1.0)的下载地址和 SHA-256：

```text
wom-api[system-certs] @ https://github.com/putianyi889/wom-api/releases/download/v0.1.0/wom_api-0.1.0-py3-none-any.whl#sha256=dfdf16a53c9a2933ff10069b7d81323cc6ac3436b7eaa12acf9cb9350aa911f8
```

网站部署 workflow `.github/workflows/build.yml` 在 tag 推送时先下载 wheel；`pip download --no-deps` 验证下载地址中的固定哈希，只下载 WOM 包。随后生成 `wheels/SHA256SUMS`，通过已有 SCP 步骤将 `wheels/` 随前端 `dist/` 上传到 `/root/github/saolei_website/back_end/saolei/`，再在服务器校验文件。下载、校验或上传失败会使相应步骤失败。文档部署 workflow 继续负责文档产物，避免两份部署流程重复维护 wheel。

上传步骤只复制和校验文件，不安装依赖、修改数据库或重启服务。服务器不需要访问 GitHub/Gitee 获取 WOM 包；其余 PyPI 依赖仍通过服务器原有索引（例如阿里云镜像）安装，不是全部依赖离线分发。`wheels/` 已由项目 `.gitignore` 忽略，不提交 wheel 二进制。升级 WOM 时同时更新两份依赖清单中的版本以及下载地址、固定哈希。

开发端在后端目录先下载 wheel，再安装依赖；后端测试、安全检查及 E2E workflow 使用同样流程：

```powershell
.\.venv\Scripts\python.exe -m pip download --no-deps --dest wheels -r requirements-wheels.txt
.\.venv\Scripts\python.exe -m pip install --find-links wheels -r requirements.txt
```

生产端在 workflow 上传完成并更新后端源码后，在服务使用的 Python 环境中校验和预演安装：

```bash
cd /root/github/saolei_website/back_end/saolei
sha256sum -c wheels/SHA256SUMS
```

只有校验成功才继续：

```bash
python3 -m pip install --dry-run --find-links wheels -r requirements.txt
```

预演打印 `Would install`，不实际安装；核对是否涉及现有依赖变更后，再安排正式部署：

```bash
python3 -m pip install --find-links wheels -r requirements.txt
python3 manage.py migrate accountlink
```

随后按原有方式重启后端并刷新 WOM 关联资料。迁移已在本地 MySQL 测试数据库执行，未应用到用户实际数据库或生产环境；新的部署 workflow 尚未在 GitHub 或生产环境运行。

本次分发流程已在本地验证：按 `requirements-wheels.txt` 下载成功且固定哈希匹配，`--no-index --no-deps --ignore-installed` 安装预演通过 `--find-links wheels` 找到 WOM 0.1.0；workflow YAML 解析、各运行脚本的 `bash -n`、校验清单生成及 `sha256sum -c` 均通过。该预演只验证 WOM wheel 的本地解析，不代表完整生产依赖安装已通过。

分发方案依据：2026-10-14 本机 pip 访问 [Gitee 同步发布](https://gitee.com/putianyi889/wom-api/releases/tag/v0.1.0)直链返回 HTTP 403，禁用缓存也未解决；用户提供的生产端日志确认相同错误，发生在 wheel 下载阶段。阿里云 PyPI 镜像不负责 Gitee 直链。具体拒绝原因未确认，不能仅凭 403 判定为 User-Agent 或防盗链规则。本机 curl 跟随正常重定向下载成功，SHA-256 与 GitHub 发布包一致，但不能证明生产端 pip 直链可用，因此改由 GitHub runner 下载和校验后通过 SCP 分发。使用 pip 的标准 [下载](https://pip.pypa.io/en/stable/cli/pip_download/)与[本地包查找](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-f)机制，不关闭 TLS 验证。

WOM 专项 Django 测试覆盖客户端释放、错误映射、空值、单位、按字段范围拒绝越界、64 位累计用时、真实数据库保存及 API Schema。本轮将重复的累计用时边界检查合并到数据库用例，耐力默认值集中在默认值与空成绩用例中，13 项专项测试及相关文件 flake8 通过；与 MSGames 和任务管理的关联回归共 53 项通过。接入时另已通过 7 项后端静态安全测试，并在网站 Python 3.12 环境中通过同步适配器实际匿名读取新增字段。系统检查仍报告既有的缺少 `dist/` 和重复 API namespace 警告。

前端 lintfix 和 typecheck 的上一轮检查已确认退出码为 0，lintfix 有 4 个既有组件测试文件警告。耐力默认值调整后的检查按跨轮流程启动，状态见当轮交付。没有运行 Cypress，组件回归命令留给用户：

```powershell
npx.cmd cypress run --component --browser chrome --headless --spec "src/components/accountlinks/CardWoM.cy.ts"
```

## 调查证据及边界

库是非官方 Alpha 客户端，236 个入口来自网站前端版本 1036，不是稳定的官方 API。对应发布提交的 [CI](https://github.com/putianyi889/wom-api/actions/runs/38416098635) 和[发布工作流](https://github.com/putianyi889/wom-api/actions/runs/38416102911) 成功。最初调查在临时检出的源码上通过 276 项库测试。

下载的[网站前端包](https://minesweeper.online/js/index-1036.js) SHA-256 为 `c0775a0a46463a382354e9bd2ba93e095864ade6c6aeb746b968db208ff30463`，与库元数据一致；本次耐力等编码依据该包核对。公开详细资料样本约 13.2 KB。当前旧 HTML 抓取使用的 XPath 在下载的玩家页面中匹配为 0，新客户端避免依赖页面布局。

源码与契约：[客户端实现](https://github.com/putianyi889/wom-api/blob/823c3b0c9c7f6477fafd3767a5ad037320cd48ee/src/wom_api/client.py)、[接口字段目录](https://github.com/putianyi889/wom-api/blob/823c3b0c9c7f6477fafd3767a5ad037320cd48ee/docs/endpoints.md)、[连接和系统证书支持](https://github.com/putianyi889/wom-api/blob/823c3b0c9c7f6477fafd3767a5ad037320cd48ee/docs/connections.md)、[协议调查](https://github.com/putianyi889/wom-api/blob/823c3b0c9c7f6477fafd3767a5ad037320cd48ee/docs/research/README.md)。

本次没有增加 WOM 录像导入。`get_game()` 返回原始 `InitGameEvent` 参数列表，实测游戏 6646633208 的快照约 724 KB，不能直接交给当前 AVF/EVF/RMV/MVF 解析器。已删除无业务调用的旧 `utils/wom.py`、`utils/wom2.py` 及其 `websocket-client` 直接依赖；WOM 公开数据获取统一使用 `wom-api`，`accountlink/wom` 保留资料映射、错误转换和测试。已删除只测试旧客户端、带固定等待与 `@skip` 的 `utils/test.py`；卡片组件的基础展示、公开成绩和累计数据合并到同一次挂载。
