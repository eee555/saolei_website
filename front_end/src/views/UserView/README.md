# 个人主页

## 路由与职责

`App.vue` 加载个人资料并提供顶级 tab，路由组件置于 `keep-alive` 中。默认进入 `/player/:id/top`，旧 `/summary` 链接重定向至 top。

| tab | 路由组件 | 数据与展示 |
| --- | --- | --- |
| top | `UserTopView.vue` | `TopSummary.vue` 请求完整 top 纪录和锚点；`TopRadar.vue`、`TopRecordTable.vue` 只渲染 props |
| PB | `UserPBView.vue` | 一次获取用户全部 PB，`PBRecordGrid.vue` 按等级展示网格 |
| 纪录 | `UserRecordView/App.vue` | 扫雷网及自定义 pluck 纪录 |
| 账号关联 | `UserAccountLinkView.vue` | 外部账号关联 |
| 录像 | `UserVideoView.vue` | 全部可见录像、日历/BV 选择、表格/散点图 |
| 上传、设置 | `UserUploadView.vue`、`UserSettingsView.vue` | 仅本人可见；设置包含资料编辑和标识管理 |

top 和 PB 的业务规则、缓存与接口统一见 [竞速排行榜 README](../../../../back_end/saolei/speedranking/README.md)，此处仅说明页面职责。

## 请求生命周期

- top、PB、设置均不下载完整录像；只有录像 tab 激活且数据失效时才请求 `videolist`。切换本地展示或返回有效缓存不重复下载。
- 页面有效性同时受激活路由、用户 id、登录会话及 `profileDataRevision` 约束。失活页面不为新玩家后台加载；过期响应不得覆盖当前玩家或清除新请求的 loading。
- 上传、标识变更通过 `profileDataService` 使相关页面数据失效，下次激活再刷新。退出或切换账号时丢弃旧身份的私有录像。
- `useProfileVideos.ts` 管理录像缓存，完整结果保存在用户页面数据中，不存入资料 IndexedDB。`userService.ts` 的 pending Promise 合并只去重并发请求，不代替结果缓存。
- 头像和签名资格读取普通扫雷网 `et`，不扫描完整录像或用 PB 最小值替代。资格查询区分加载、失败和未达标，设置页保留重试及后端最终校验。

## top 展示

- 普通/NF 各一块，每块上方雷达图、下方九项成绩表。两块用 CSS grid 自适应并列或上下排列；宽表在自身容器内横向滚动。
- 两图共用一次用户完整纪录请求和一次锚点请求。各图只使用本榜主要锚点作为 VueUiRadar 原生 target，归一化为 100；Time 反比、Bvs/iqg 正比，Stnb 仅展示时乘等级系数。超过锚点沿用图表库默认尺度，空锚点简单取半径 0。
- 不显示标题或 legend；NF 图中央通过 `#svg` 插槽显示半透明 NF。区域右上角的绝对定位刷新图标重新读取两份数据，不触发后端重建。
- 成绩表按等级合并三行，列出均值和五条成绩。缺项显示缺省值但不生成录像链接；真实录像复用 `VideoPreviewLink`。锚点失败不阻断成绩表。

## PB 展示

- 用户全部 PB 按 `(nf, level, bv)` 索引；普通/NF 和 `time / bvs / stnb / rank` 在本地单选切换，不追加请求。
- 每级别网格每行十格，按已有最小/最大 BV 向十位补齐。无纪录格子留空，整级别无纪录时显示空态；有纪录的格子预览同一条 PB 录像，不因指标变化重新选录像。
- `rank=null` 显示 `--`，不丢弃已有录像；原生 `title` 展示时间、派生指标和排名，不逐格预取详情。
- rank 前三名采用不透明金银铜和固定深色文字；4–10、11–50、51–100 名采用主题蓝的 22%、14%、7% 背景，之后及缺失排名无填色。后续排名文字使用主题色，不降低整格或链接透明度。

## 录像选择与展示

- 初始上方不显示可视化，下方显示表格。上方可选日历/BV 表，下方可选表格/散点图；散点图不依赖实验开关。
- 数据链为完整可见录像 → 日期/BV 选择 → 共享筛选 → 表格或散点图。上方始终统计完整录像，下方两种展示使用相同筛选结果；表格分页不截断散点图输入，CSV 仍导出原有完整个人数据。
- 日期使用浏览器本地年月日；结束日期模式沿用 `end_time ?? upload_time`。切换日期来源时清除日期选择，允许选择空日期。
- BV 选择使用完整 `(level, bv)` 桶，包含各模式、软件及状态。BV 表自己的代表录像筛选仅影响上方展示，不缩窄下方成员；下方共享筛选也不改变上方分布。
- 选择状态仅保存日期或 BV 键，不复制录像数组。重复点击或清除恢复全集；切换上方概览清除选择，切换下方展示保留选择、筛选和有效展示状态。用户或身份变化时重置；刷新后不存在的 BV 桶取消选择。
- 范围或共享筛选变化后表格回到第一页。主要日历/BV 操作只选择，不同时打开播放器；独立预览保留，其他未启用选择的调用方仍可直接预览代表录像。日期/BV 支持键盘选择和主题选中边框。
- 本人公开比赛录像沿用共享确认弹窗，成功后只更新该录像，失败保留状态供重试；其他用户和访客仍受后端可见性限制。

## 验证

- `App.cy.ts`：顶级 tab、默认入口、按需加载及设置权限。
- `TopSummary.cy.ts`：普通/NF 共享请求、表格明细、失活隔离及锚点失败重试。
- `UserPBView.cy.ts`：指标/NF 切换、rank 配色、空态、重试及请求生命周期。
- `useProfileVideos.test.ts`、`videoSelection.test.ts`：身份与修订号失效、过期响应、日期/BV 选择及共享筛选。
- `UserVideoView.cy.ts` 与日历/BV 组件测试：选择联动、正式散点图、分页及公开操作；`cypress/e2e/profile.cy.ts` 保留真实后端流程验证。

```powershell
# 在 front_end 目录运行
npx.cmd vitest run src/services/topRankingService.test.ts src/services/pbRankingService.test.ts src/views/UserView/useProfileVideos.test.ts src/views/UserView/videoSelection.test.ts
npx.cmd cypress run --component --browser chrome --headless --spec "src/views/UserView/App.cy.ts,src/views/UserView/TopSummary.cy.ts,src/views/UserView/UserPBView.cy.ts,src/views/UserView/UserVideoView.cy.ts"
```

Cypress 由开发者运行。实际雷达图尺度、宽窄布局和深浅主题需浏览器验收，不能用编译或静态检查通过替代。
