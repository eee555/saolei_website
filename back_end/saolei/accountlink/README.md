# Account Link

## Mineracer 接入计划

Mineracer 提供的账号关联方式不是现有的“用户手填平台 ID，管理员人工验证”流程，而是更接近 OAuth 2.0 Device Authorization Grant 的确认模型：

1. OpenMS 服务端使用 Mineracer 提供的 partner key 请求一次性 `deviceCode`。
2. Mineracer 返回一个 10 分钟有效的账号关联链接。
3. OpenMS 前端把该链接交给当前登录用户。
4. 用户在 Mineracer 站点打开链接并点击确认关联。
5. OpenMS 服务端使用 `deviceCode` 轮询 Mineracer，直到 Mineracer 确认并返回该用户的 `userId`。
6. OpenMS 使用返回的 `userId` 完成本地账号绑定。

参考标准模型：[OAuth 2.0 Device Authorization Grant](https://www.rfc-editor.org/rfc/rfc8628.html)。

### 后端工作

1. 新增平台枚举与账号模型

   在 `models.py` 增加 `Platform.MINERACER`。现有 `AccountLinkQueue.platform` 是 `max_length=1`，因此建议使用单字符平台码，例如 `m`。同时新增 `AccountMineracer`，最小字段包括：

   - `id`：Mineracer 返回的 `userId`，这是 9 位或 17 位字符串。
   - `parent`：指向 `UserProfile` 的一对一关联，`related_name` 可命名为 `account_mineracer`。
   - `update_time`：本地同步或绑定更新时间。

   新模型需要加入 `PLATFORM_CONFIG`。等模型结构稳定后，再通过 Django 命令自动生成迁移脚本。

2. 使用 Redis 保存 Mineracer 临时会话

   现有 `AccountLinkQueue` 只能表达 `platform + identifier + verified`，无法表达第三方确认中的临时状态。但 Mineracer 关联会话只有 10 分钟有效，且只是服务端轮询所需的临时状态，因此不新增数据库会话模型，改用 Redis cache 保存一次关联尝试。

   项目里已有两个 Redis cache alias：`saolei_website` 用于 Django session，`default` 使用 `redis://127.0.0.1:6379/1`。Mineracer 关联会话固定使用 `caches['default']`，避免和登录 session 共用 alias。

   Redis session 内容包括：

   - `user_id`：OpenMS 当前登录用户 ID。
   - `device_code`：Mineracer 返回的 `deviceCode`，只在服务端保存。
   - `user_code`：Mineracer 返回的 `userCode`。
   - `verification_uri`
   - `verification_uri_complete`：提供给用户打开的完整确认链接。
   - `expires_at`
   - `status`：`pending`、`confirmed`、`expired`、`failed`
   - `remote_userid`
   - `last_polled_at`
   - `next_poll_at`
   - `error_category`

   推荐 key 设计：

   - `accountlink:mineracer:session:{session_id}`：保存完整临时会话，TTL 为 Mineracer `expiresAt` 到期时间加少量 grace 时间，用于前端在刚过期或刚完成后还能读到终态。
   - `accountlink:mineracer:user:{user_id}:pending`：保存当前用户的 pending `session_id`，TTL 到 `expiresAt`，用于重复点击 start 时复用同一个会话。
   - `accountlink:mineracer:user:{user_id}:start_lock`：短 TTL 锁，避免并发创建多个 Mineracer 链接。
   - `accountlink:mineracer:session:{session_id}:poll_lock`：短 TTL 锁，避免多个 OpenMS 进程同时拿同一个 `deviceCode` 去 Mineracer poll。

   绑定成功后再写入数据库：`AccountMineracer.id` 和 `AccountLinkQueue.identifier` 都保存 Mineracer `userId`，`AccountLinkQueue.verified=True`。临时会话不需要迁移。

3. 使用日志做审计记录

   不新增审计表。Mineracer 关联流程的审计记录写入现有 `accountlink` logger，对应 `logs/accountlink.log`。建议记录：

   - start 创建、start 复用、start 拒绝。
   - poll 发送、poll pending、第三方请求临时失败。
   - confirmed、expired、failed、identifier_conflict。

   日志字段应包含 OpenMS `user_id`、Redis `session_id`、状态、错误分类和确认后的 Mineracer `userId`。不要记录 partner key，也不要完整记录 `deviceCode`。

4. 新增 Ninja API

   按项目约定，新 API 放在 `accountlink/api.py`。Mineracer 独占逻辑集中在 `accountlink/mineracer/`，API 层只做登录、限流后的入口转发和响应组装。

   - `POST /api/accountlink/mineracer/start/`
     - 登录用户调用。
     - 检查当前用户是否已有关联中的 Mineracer 会话或已绑定 Mineracer 账号。
     - 使用服务端 partner key 请求 Mineracer。
     - 保存 Redis 临时会话，返回 `session_id`、`verification_uri_complete`、`expires_at`、`next_poll_at`。

   - `GET /api/accountlink/mineracer/status/{session_id}`
     - 登录用户调用，只允许读取自己的会话。
     - 如果未到 `next_poll_at`，直接返回本地状态，避免每次前端轮询都请求 Mineracer。
     - 到达轮询时间后请求 Mineracer 状态接口。
     - 如果 Mineracer 返回 `userId`，则在事务中完成绑定。

   绑定成功时需要检查冲突：同一个 Mineracer `userId` 如果已经被其他 OpenMS 用户验证绑定，应返回 409。

5. 新增 Mineracer HTTP 客户端封装

   在 `accountlink/mineracer/client.py` 中封装：

   - 请求 `deviceCode` 和确认链接。
   - 轮询关联状态。
   - 将 Mineracer 错误码映射为本项目已有的 `ExceptionToResponse` 风格分类。

   `accountlink/mineracer/dtos.py` 放 Mineracer 状态常量和 dataclass；`accountlink/mineracer/sessions.py` 放 Redis 会话、轮询状态机、最终绑定和审计日志。partner key、API base URL、timeout、轮询间隔等配置不能进入前端，需放在服务端配置中。

   Mineracer 当前接口约定：

   ```http
   POST https://mineracer.com/api/partner/link/start
   Authorization: Bearer MINERACER_ACCOUNT_LINK_PARTNER_KEY
   ```

   start 请求不需要 request body。成功响应：

   ```json
   {
     "deviceCode": "PRIVATE_REQUEST_CODE",
     "userCode": "ABCD-EFGH",
     "verificationUri": "https://mineracer.com/link",
     "verificationUriComplete": "https://mineracer.com/link?code=ABCD-EFGH",
     "intervalMs": 2500,
     "expiresAt": 1780000000000
   }
   ```

   `deviceCode` 只保存在 OpenMS 服务端；前端使用 `verificationUriComplete`，不需要单独展示 `userCode`。

   ```http
   POST https://mineracer.com/api/partner/link/poll
   Authorization: Bearer MINERACER_ACCOUNT_LINK_PARTNER_KEY
   Content-Type: application/json
   ```

   请求体：

   ```json
   {
     "deviceCode": "PRIVATE_REQUEST_CODE"
   }
   ```

   Mineracer 在等待用户确认时返回 HTTP 202；用户确认后返回 HTTP 200：

   ```json
   {
     "status": "linked",
     "userId": "STABLE_MINERACER_USER_ID"
   }
   ```

   OpenMS 应使用 `intervalMs` 控制本地 `next_poll_at`，不要让前端每次 status 请求都触发第三方 poll。

6. 兼容现有通用逻辑

   - `delete_account` 需要支持删除 Mineracer 账号关联。
   - `link_account` 可以继续复用，但要确认 `AccountMineracer.id` 类型和 Mineracer `userId` 类型一致。
   - `update_account` 是否支持 Mineracer 取决于对方是否提供资料或统计 API。若暂时没有资料 API，可以先不提供同步按钮。
   - `get_account_links` 的输出 schema 需要包含 Mineracer 账号详情字段。

### 前端工作

1. 平台基础信息

   更新 `front_end/src/utils/accountlinks/platforms.ts`：

   - 增加 `AccountLinkPlatform.Mineracer`。
   - 增加 Mineracer 官网地址与 profile URL 生成函数。

   同时更新中英文 `common.platform` 翻译。

2. 数据类型

   新增 `mineracer.ts`，定义 `AccountMineracerResponse` 和 `AccountMineracer`。更新 `collection.ts` 的 `AccountLinksResponse` 与 `AccountLinks`，使账号页能承载 Mineracer 数据。

3. 添加账号交互

   当前 `CardAdd.vue` 对所有平台都要求用户输入数字 ID。Mineracer 需要单独分支：

   - 用户选择 Mineracer 后，不显示 ID 输入框。
   - 显示“生成关联链接”按钮。
   - 成功后显示外链按钮、过期倒计时和当前状态。
   - 前端定时请求本项目的 status API。
   - 后端确认成功后刷新账号关联列表。

4. 展示卡片

   新增 `CardMineracer.vue`，并加入 `App.vue` 的 `accountCardConfigs`。最小版本只需显示 Mineracer `userId`、验证状态和绑定时间。若 Mineracer 后续提供公开资料或统计接口，再补摘要数据和同步功能。

5. 文案与错误处理

   在中英文 locale 中增加：

   - 生成关联链接
   - 链接已过期
   - 等待 Mineracer 确认
   - 关联成功
   - 第三方确认失败
   - 账号已被其他用户绑定

   Mineracer 状态接口的错误分类应在 `accountLinkService.ts` 中集中映射，延续现有账号同步错误处理方式。

### 安全与一致性要求

1. partner key 只在服务端使用，通过 `MINERACER_ACCOUNT_LINK_PARTNER_KEY` 配置，不进入构建产物和接口响应。
2. start/status API 都需要登录校验与限流。
3. status API 必须校验会话归属，不能让用户查询或完成他人的会话。
4. Redis 临时会话必须使用 `default` cache alias，不能放进 `saolei_website` session cache。
5. 绑定成功逻辑应放在数据库事务中，并锁定相关记录，避免并发重复绑定。
6. 过期会话不能继续绑定；如果 Mineracer 返回过期状态，本地也应标记为 expired。
7. 前端打开 Mineracer 链接时使用新窗口，并使用 `rel="noopener noreferrer"`。
8. 审计记录使用 `accountlink` 日志；日志中不要记录 partner key，也不要完整记录可复用的 `deviceCode`。

### 需要向 Mineracer 确认的问题

1. 一个 Mineracer 账号是否允许绑定多个 OpenMS 账号；如果不允许，是否由 Mineracer 拒绝还是由 OpenMS 拒绝。
2. 用户取消、`deviceCode` 过期、重复确认时的返回状态与错误响应格式。
3. 是否支持确认后 redirect 回 OpenMS 账号关联页。
4. 是否提供测试环境或测试账号。
5. 解绑时是否需要 OpenMS 通知 Mineracer。

### 推荐实施顺序

1. 配置 `MINERACER_ACCOUNT_LINK_PARTNER_KEY`，确认测试环境或生产环境联调策略。
2. 后端实现 `AccountMineracer`、Redis 临时会话和 Mineracer HTTP 客户端；迁移等模型结构稳定后再生成。
3. 后端实现 start/status API，并覆盖成功、过期、冲突、重复发起、会话越权、Redis TTL/锁等测试。
4. 前端实现 Mineracer 添加流程、轮询状态和最小展示卡片。
5. 更新中英文文案和组件测试。
6. 与 Mineracer 联调测试环境，确认 10 分钟过期、确认成功、冲突账号、取消/失败路径。
7. 部署后观察日志、第三方请求失败率和用户绑定成功率。
