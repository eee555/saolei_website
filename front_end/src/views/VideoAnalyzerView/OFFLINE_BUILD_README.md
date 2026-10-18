# VideoAnalyzer 离线构建调查

调查及本地构建日期：2026-10-12。本地文件入口和离线构建已实现，首次本地 ZIP 已生成；独立 Actions 工作流及真实浏览器 file:// 验收尚未完成。

## 本地生成与打开

在 `front_end` 执行 `npm.cmd run build:offline`。产物为 `OpenMinesweeperVideoAnalyzer-${version}.zip`，版本来自 `local-analyzer/version.json`，展开目录为 `dist-offline-analyzer/`；ZIP 根目录包含 `index.html`、`README.txt`、`version.json` 及中英文 `help/`，没有二次嵌套 ZIP。解压后双击 `index.html`，在 info slot 选择或拖入一份录像。也可直接打开展开目录中的 HTML。

Analyzer 使用独立版本，唯一来源为 `local-analyzer/version.json`；离线 info slot 直接显示当前版本，ZIP 复制同一份文件。修改前遵循 [版本管理约束](../../../local-analyzer/VERSIONING.md)，并同步 [更新记录](../../../local-analyzer/CHANGELOG.md)；网站 tag、网站其他功能修改和重复构建不自动递增 Analyzer 版本。

离线页面的信息区版本号旁和浏览器标签页使用定制 Analyzer 图标，复用 `src/assets/video-analyzer.svg`，经 Vite 内联为 SVG 数据 URL，不需要在 file:// 下加载外部图片。打包脚本要求 favicon 已内联。录像页的离线包下载按钮使用同一图标。接入图标的离线版本为 0.1.2。

info slot 内的文件选择区下方提供 README 和 COPYRIGHT 两个原生 details，初始收起，点击或键盘操作 summary 可独立展开。内容从 `local-analyzer/README.txt` 和 `local-analyzer/COPYRIGHT.txt` 内联，打包脚本复制同一份源文件；查看正文不需要 file:// fetch。展开后说明区内部滚动，继续沿用 Analyzer 的宽窄容器布局。

说明区右侧提供 English / 中文 按钮，切换公共 i18n 的界面语言，并保存到轻量 local 设置；下次启动离线入口时恢复选择。切换不重新解析录像或重置播放位置，README/COPYRIGHT 正文仍为包内双语原文。

站内录像页的网站信息按钮组提供下载图标，目标为 `${BASE_URL}assets/OpenMinesweeperVideoAnalyzer-${version}.zip`，下载文件名使用相同版本，不依赖当前录像或信息请求成功。离线打包同时生成 `public/assets/OpenMinesweeperVideoAnalyzer-${version}.zip`；三个网站 build 脚本及 dev/frontend 启动均通过 npm pre hook 先构建离线包，Vite 再将 ZIP 复制到 `dist/assets/`。现有 tag 部署工作流沿用 `build:openms`，会随网站发布 ZIP；独立离线 artifact 工作流仍待接入。直接执行 Vite CLI 时应先手动运行 `npm run build:offline`。

部署时，`collectstatic` 将 ZIP 收集到 `/root/saolei/static/assets/`。`back_end/saolei/default.conf` 通过 `location ^~ /assets/` 直接提供该目录下的全部 Vite 资源，避免 ZIP 因不在静态扩展名列表中而被转发给 Django、返回 404。服务器须同步该配置到 `/etc/nginx/conf.d/default.conf`，执行 `nginx -t` 后重载；仅重新打包网站不会更新已加载的 Nginx 配置。发布后用 `curl -I https://openms.top/assets/OpenMinesweeperVideoAnalyzer-<version>.zip` 核对状态码 200 和 `Content-Type: application/zip`，并实际下载检查包内版本。仅修复服务器路由或本文部署说明时不递增 Analyzer 版本。

网站“软件下载”弹窗另有 Analyzer 标签页，使用定制图标和版本/日期/下载表格。发布历史保存在 `src/components/dialogs/AnalyzerHelper.vue` 的 `tableData`，按实际提供下载的包手动添加记录；不读取 `version.json` 自动更新。标签页展示已有离线包，不改变 Analyzer 版本。交互检查由用户运行：`npx.cmd cypress run --component --browser chrome --headless --spec "src/components/Footer.cy.ts"`。

本轮主 HTML 约 2.84 MB、ZIP 约 0.94 MB。构建检查确认主脚本、CSS、WASM 和字体已内联，没有独立资源文件；依赖图不包含网站包装页、网站 store、HTTP 初始化或路由。包内帮助由现有中英文 Markdown 生成。上述检查与 26 项相关单元测试通过，不能代替断网、无缓存的 file:// 运行及实际视频导出验收。本轮未运行浏览器或 Cypress。

版权文件随 ZIP 根目录提供：`LICENSE` 原样复制项目 MIT 声明，`COPYRIGHT.txt` 提供项目归属和来源，`THIRD_PARTY_LICENSES.txt` / `.json` 包含实际打包依赖的完整声明，`licenses/` 保留字体和共享 CSS 的声明。依赖列表复用 [Vite build.license](https://vite.dev/config/build-options.html#build-license)，在单文件插件删除 JS chunk 之前收集；打包时拒绝空列表及缺失正文。本次 30 项依赖的声明及项目原文均已从最终 ZIP 核对。`ms-toollib@1.5.19` 的 npm 包没有 LICENSE，使用 `front_end/licenses/ms-toollib/` 的上游副本补充，升级版本时必须重新核对。

供用户运行的组件测试（在 `front_end`）：

```powershell
npx.cmd cypress run --component --browser chrome --headless --spec "src/views/LocalVideoAnalyzerView/App.cy.ts,src/components/VideoAnalyzer/ProgressBar.cy.ts,src/components/VideoAnalyzer/TimelinePanel.cy.ts,src/components/VideoAnalyzer/VideoExport.cy.ts"
```

组件测试通过后仍需直接打开离线 HTML，断网检查四种格式、连续更换文件、播放/布局/图层、帮助链接及短视频导出。浏览器许可、存储、剪贴板和编码器能力在 file:// 下尚待确认。

方案更新：用户已决定移除 Worker 并行导出，当前仅保留主线程导出。离线包不再需要 Worker 子构建、内联 Worker 或多线程验收；WASM、SVG、字体及动态模块仍须内联并通过 file:// 验证。

## 目标

用户已确认：解压后双击主 HTML，首次断网也能运行；不能要求本地 HTTP 服务或提前在线缓存。VideoAnalyzer 保留为项目内组件，共享项目 CSS/i18n，由网站和本地文件页面共同调用。离线入口不请求站内 API。

页面差异仅在 `info` slot：离线入口将网站信息替换为选择录像文件的控件，选择 EVF/AVF/MVF/RMV 后读取字节，作为 ReplaySource 传给同一个 VideoAnalyzer。棋盘、计数器、时间轴、布局和导出全部复用；不新增顶部文件工具栏、独立文件信息面板或外部分析链接列。选择区沿用 slot 的布局：宽容器与计数器共享面板，窄容器置顶；导出期间禁止换文件。

## 已有实现可以复用什么

| 当前实现 | 用途与需要调整的地方 |
| --- | --- |
| components/VideoAnalyzer/App.vue / useReplaySource.ts | 公共分析组件已提取；接收普通 ReplaySource，按实例持有解析对象、时钟及采样；本地页面可直接复用，不导入网站包装页。 |
| views/VideoAnalyzerView/App.vue / useSiteReplaySource.ts | 网站包装页已分离：站内请求、分析区域可访问名称及信息 slot、配置持久化、概率配色绑定和路由守卫；离线页直接包装公共组件，slot 换成文件选择。 |
| replayParser.ts / ReplaySource | 已支持四种录像及失败时 free；适合作为两种输入共用的解析入口。 |
| BaseFileInput / useLocalReplaySource.ts | 复用文件选择和拖入控件，补充单文件选择参数；四种格式大小写扩展名、读取失败、替换及迟到读取的处理已实现，不复制解析流程。 |
| App.vue / CounterPanel.vue | 信息 slot 已由公共组件提供，宽容器与计数器共享面板并自动布局，窄容器置顶；离线页在该 slot 内提供文件选择控件，沿用现有布局。网站信息及 `--` 不进入离线入口。 |
| BoardPanel.vue / VideoExportControls.vue | 概率配色与导出设置已通过 model 传入，不再直接读取网站 store 或 Analyzer 配置单例；仍复用项目通知和剪贴板 helper。 |
| boardExportFrame.ts / exportReplayState.ts | 复用主线程独立解析、定位、渲染和裁剪合成；沿用独立解析对象释放及帧 release / 渲染器 destroy。 |
| vue-tippy / 共享基础组件 | 保留现有 UI，tooltip 源节点初始 hidden 的修复一并迁移；不新建第二套 UI 库。 |
| i18n / CSS | 在独立 main.ts 直接初始化必要资源，不导入网站 main.ts 或根 App。 |
| Notifications / CopyToClipboard | 所需 local 设置已移到 store/local.ts，原 store 路径重导出兼容；离线入口不加载用户 store。剪贴板继续调用 navigator.clipboard，需真实 file:// 验证。 |
| CounterExpressionHelp / getDocsUrl | 离线构建使用包内相对 HTML 路径，静态中英文帮助由现有 Markdown 生成；网站帮助地址保持原规则。 |

## 构建方案比较

| 方案 | 判断 |
| --- | --- |
| 普通 Vite dist + 相对 base | 不作为交付方案；相对路径并不能保证 file:// 的 module 和 fetch 加载可用。 |
| 附带本地服务器启动脚本 | 用户已明确不采用。 |
| PWA / Service Worker 缓存 | 不作为首次离线启动的前提。 |
| Vite 单 HTML + 内联 WASM/贴图 | 本地构建已成功；使用 vite-plugin-singlefile 2.3.3，继续保留真实浏览器验收。 |

`vite-plugin-singlefile` 提供把主 JS/CSS 放进 HTML 的现成方案，适合单一 HTML 入口；不会负责把 public 目录任意资源内联，对 SVG 也不能仅凭 README 作保证。其推荐配置会设置资源内联及合并输出，但本项目的 Vite 8 和已发布棋盘包仍须检查真实产物。[项目 README](https://github.com/richardtallent/vite-plugin-singlefile)、[推荐配置源码](https://github.com/richardtallent/vite-plugin-singlefile/blob/main/src/index.ts)

本地安装的 vite-plugin-wasm 已确认两条加载分支：`dist/wasm-helper.js` 对 base64 data URL 直接解码并 WebAssembly.instantiate，其他 URL 使用 fetch；`dist/index.js` 在浏览器构建通过 `?url` 取得 WASM 资源。因此主入口必须把 WASM 变成数据 URL，而不是留下独立 wasm 文件再从 file:// fetch。Vite 提供资源内联设置，是否全部内联须以产物和浏览器验证为准。[Vite 资源内联设置](https://vite.dev/config/build-options.html#build-assetsinlinelimit)

棋盘继续使用 0.6.1 的主线程独立渲染器。检查嵌入的 SVG data URL、第一次使用数字/旗/雷的贴图、半透明轨迹和光标；不绕过库改写棋盘绘图。PrimeIcons 的字体和 CSS url 也必须嵌入。

首次构建发现 PrimeIcons 的历史 SVG 字体引用带 fragment，Vite 会保留外部资源。离线配置通过 PostCSS 修改该 font-face 的 src，仅保留 Chrome/Edge 使用的 WOFF2 字体，再交给 Vite 内联；完整图标类继续来自原库。此调整只作用于离线构建，不修改依赖或网站字体。`package-offline-analyzer.mjs` 在打 ZIP 前拒绝独立资产、外部脚本/样式及非内联 CSS 资源，并要求内联 WASM。

## 最小原型要回答的问题

- 主 HTML 能否在 file://、断网且无旧缓存时完成 WASM 初始化，并解析已有 fixture？
- 主线程独立解析和导出能否在相同环境使用内联贴图并生成有效视频？
- 产物是否仍含需要访问外部文件的 module、WASM、字体、CSS、图片或动态 import？不能把 SVG namespace 和用户主动打开的文档链接误判为资源请求。
- 同一设置下，在线与离线的画面、帧序、倍率及导出结果是否一致？file:// 下存储、剪贴板、Blob 下载及编码能力如何表现？
- 插件与本项目 Vite 8 的配置/类型是否兼容？如不兼容，先调查或修复插件接线，不用手写字符串替换绕过打包器。

## 工作流交付

当前 frontend.yml 主要验证站内构建，build.yml 在 tag 下还会拉取其他项目和使用部署密钥上传生产网站。离线包使用独立配置、输出目录及 workflow，锁文件安装、构建、检查后上传 artifact，不经过生产部署。

Actions 下载的 ZIP 解压后应直接得到主 HTML 和包内静态帮助/说明。先提供 artifact；本阶段不默认创建 GitHub Release 或发布独立 npm 包。实现时同时更新中文/英文用户说明，保留已有后台和网站入口。

详细实施进度见 [PLAN.md](./PLAN.md)，已实现的组件接口见 [VideoAnalyzer 使用说明](../../components/VideoAnalyzer/README.md)。
