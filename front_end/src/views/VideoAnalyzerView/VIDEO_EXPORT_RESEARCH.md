# 棋盘视频与动图导出调查

调查日期：2026-10-10。原调查基于源码、官方文档和 npm 发布信息；后续视频验证首版的接入进度见下一节。本次未运行浏览器性能或画面测试，不代表已确认全部浏览器可用。

状态复核日期：2026-10-11。此前功能已有用户手动粗测记录，不包含本轮 Worker 路径，组件测试在 feature 完成后统一运行；本轮核查 0.6.1 发布包并接入多线程导出，未重新验证原调查的全部候选库。

## 当前方案

导出组件测试位于 [src/components/VideoAnalyzer/VideoExport.cy.ts](../../components/VideoAnalyzer/VideoExport.cy.ts)，直接向公共 Analyzer 传入真实录像字节及实例配置，不依赖网站信息接口或配置单例。

2026-10-12 用户决定移除 Worker 并行导出。当前仅使用主线程独立解析、棋盘渲染、裁剪合成及 Mediabunny 编码；并行模式选择、线程池、协议和对应测试已删除，格式/帧率/质量及取消/恢复行为保留。浏览器编码器内部调度由 WebCodecs 决定。本项目不接入多个编码器分段拼接；离线构建方案同步取消内联 Worker 需求。

组件测试默认由用户运行，代理每轮只启动 lintfix / typecheck 并在下一轮开始读取结果。以下记录接入与优化的历史过程，包括已撤销的 Worker 方案，不能作为当前功能或验收状态。

## 历史接入记录

2026-10-12 用户环境反馈：AMD Ryzen 4800H、NVIDIA GTX 1660 Ti、Windows 11、最新 Chrome；兼容模式可用，自动及显式并行模式进度不动，控制台没有错误。当前没有证据关联 DTS 音频处理进程；本导出链路仅处理棋盘图像，不创建音频轨道。尚未确认反馈来自开发页面还是部署页面，也未取得用户设备的 Network 记录。

源码中主线程创建 Worker 后立即发送 init，而 `ms-toollib` 的 WASM 导入经插件使用 top-level await；Worker 的 onmessage 在依赖完成后才安装，早到的初始化消息可能丢失，主线程无超时地等待 ready。这是当前发现的具体竞态，与反馈吻合，尚未在用户设备证明它是唯一原因。[Vite 官方文档](https://vite.dev/guide/features.html#webassembly) 说明 WASM 模块的异步初始化；[Deno 维护者对同类消息丢失的说明](https://github.com/denoland/deno/issues/14098) 和 [Comlink 的 Chromium 复现](https://github.com/GoogleChromeLabs/comlink/issues/635) 提供可对照的上游案例。

本轮在既有协议中增加 loaded → init → ready：监听器安装后主动握手，池记录已启动状态，贴图复制完成且已握手后才发送一次 init。启动与录像初始化共用 60 秒等待上限，超时拒绝 Promise 并清理全部 Worker，界面恢复操作并给出错误；取消不等待超时。准备阶段明确显示“正在准备视频”。不使用固定 sleep、不重复传输资源、不静默退回兼容模式。

新增单元检查握手前不发送、提前握手、重复 loaded 不重复 init、未启动和已启动后解析超时清理。相关 4 个单元文件共 30 项通过；原生 Worker 对照测试加入延迟 WASM 响应以覆盖启动竞态，实际成品及主线程/Worker 画面对照按跨轮流程启动 Cypress，结果待下一轮检查。仍需用户设备复核进度、取消、通知和成品。

2026-10-10 已接入 Mediabunny 1.61.3 与 minesweeper-board 0.6.0 的独立渲染接口，提供棋盘整段/区间视频导出。最初使用的 modern-screenshot 4.7.0 已移除；GIF、FFmpeg.wasm、APNG 均未接入。下文保留原始调查及候选对比。

首版提供 MP4/WebM/MOV/MKV，按实际裁剪尺寸、帧率和质量检测可用编码器；默认 MP4、30 FPS、高质量。显式帧时间戳、逐帧背压、取消清理及 BufferTarget 成品下载已接入；使用原生模态窗口冻结页面操作，固定实际格子大小，结束后恢复播放位置和状态。使用 BufferTarget 仍需保存全部编码结果，不能据此承诺长录像的内存上限。

单元测试验证的是调度、合成及清理，不证明浏览器能编码或实际画面完全一致。2026-10-11 本轮 Analyzer 的 16 个单元测试文件共 217 个测试通过，类型检查和生产构建通过。`VideoExport.cy.ts` 使用真实 EVF 导出短 MP4/WebM 再解码检查尺寸、时长、帧数和非空画面，以及取消和输入限制；该测试在 feature 完成后由用户统一运行。用户已粗测此前功能，系统性画面对比及分阶段性能测试仍待进行。本轮将按键事件并入轨迹，页面和导出共用全部线宽、状态线色及 marker props；这些新增设置的画面尚待用户粗测。

当前导出从已经下载的文件字节创建独立解析对象，不重新请求录像，不推进页面 `currentMs`，不逐帧刷新可见棋盘、计数器及时间轴，也不等待 Vue 更新。`boardExportFrame.ts` 将当前帧数据交给独立渲染器，等待贴图解码完成，直接合成到裁剪后的编码 Canvas。不使用 DOM 截图或 requestAnimationFrame。全局层在一次导出中仅渲染一次；SVG 光标移除 DOM 热点 transform 后仅解码一次，每帧按导出坐标计算同一热点。各层按背景、全局、已打开、概率、轨迹、光标顺序合成并应用各自不透明度。每帧消费后 release，完成、失败或取消时 destroy 并释放独立 WASM 对象；进度约每 50ms 刷新一次并让出主线程响应取消，不等待媒体帧间隔。

### 导出速度与优化进度

用户实际反馈原流程导出过慢，原来每帧的两次 requestAnimationFrame 等待和 DOM 截图均有明确开销，但未做分阶段性能实测，不能认定编码器是主因。

第一步曾按 [modern-screenshot 官方的上下文复用方式](https://github.com/qq15725/modern-screenshot#singleton-context-and-web-worker) 减少重复初始化。该实现及其截图测试现已删除，改由 `boardExportFrame.test.ts` 检查合成、缓存及资源清理，`boardExportFrame.cy.ts` 检查真实图层和圆点/Windows SVG 光标的移动、热点及裁剪。浏览器测试由用户运行。

第二步使用 0.6.0 的公开独立渲染接口替换截图，未扫描私有 DOM 或重写依赖绘图，原接口需求已满足。当时仅在主线程执行；此后曾增加 Worker 路径，现已按用户决定移除。精确画面、MOV/MKV 成品和长录像内存仍待验证。

第三步针对“导出耗时接近成品播放时长”的反馈，移除了逐帧页面定位及 Vue 刷新。Mediabunny 1.61.3 的 `CanvasSource.add` 源码只在编码队列达到 4 或封装写入需要背压时等待，没有按帧时间戳等待真实时间的逻辑。现在通过公开 `canEncodeVideo` 使用实际尺寸、帧率、质量及 `prefer-hardware` 检测并优先选择硬件候选；无候选时回退到 `no-preference`。探测与实际编码使用相同硬件偏好，保持 `latencyMode: 'quality'`，不为低延迟而允许丢帧。硬件偏好是浏览器提示，不能证明实际使用了硬件，也不保证速度提升。成品播放倍率仅决定录像取样位置、帧数及成品时长，处理按渲染和编码器吞吐推进。单元测试已覆盖无需推进真实时钟即可提交一分钟视频及硬件候选优先/回退，实际吞吐仍需同参数性能对比。

第四步曾升级 0.6.1 并接入多线程首版，现已移除。下述仅记录该方案：主线程一次栅格化贴图和光标，各 Worker 独立位图、文件字节副本、解析、定位、渲染和 OffscreenCanvas 合成/裁剪。最终帧 ImageBitmap 转移到主线程，按编号消费并关闭，Mediabunny 继续有序编码和背压。每 Worker 最多一帧未消费任务，缓存结果也占名额，防止慢帧导致无界积压。完成/取消/失败关闭缓存并终止 Worker。

导出支持自动、兼容及 1/2/4 路。自动按设备取 1 至 4 路，缺少基础能力走主线程；显式并行或实际 Worker 失败明确报错，可用兼容模式重试。两条路径共用定位及合成，冻结设置和实际 size；不传函数、DOM 或 WASM 包装对象，棋盘事件 SVG 图层仍排除。Vite Worker ES/wasm 配置和生产构建已检查，WASM 仍有 top-level await 提示，依赖现代浏览器能力；开发环境真实 Worker 和实际成品留给用户运行组件测试。

该 Worker 请求已由上游 0.6.1 满足，但本项目的并行导出已撤销，过时请求文档已删除。原始 CPU 反馈尚未分阶段实测，不承诺固定提速。
单 Worker 移出主线程不等于多核并行；多 Worker 的有效并发数、传输成本、峰值内存及实际速度需要同参数实测。保留主线程兼容路径，不为提速改变成品倍率、丢帧或预先保存所有帧，也不因 CPU 反馈直接引入 FFmpeg.wasm 或多编码器拼接。

## 结论

- 视频优先采用 Mediabunny：逐帧提交合成 canvas 和显式时间戳，可覆盖 MP4、WebM、MOV、MKV，另可评估 MPEG-TS；格式和编码器必须按实际输出尺寸、帧率及浏览器能力筛选。[支持矩阵](https://mediabunny.dev/guide/supported-formats-and-codecs)
- GIF 独立编码。gifenc 在逐帧处理及内存控制方面更合适，但发布类型有缺口，接入前需解决；modern-gif 类型完整，可作为候选，但不适合不加验证地用于长录像。两者具体差异见下文。
- 完整画面合成已采用棋盘依赖公开的独立渲染接口和 Canvas drawImage；不使用实时录屏插件代替确定时间戳的导出。下面的 DOM 截图库对比保留为历史调查，不再是当前导出路径。
- FFmpeg.wasm 保留为按需加载的扩展方案，用于浏览器原生编码缺失或其他格式。APNG 可评估 UPNG.js；动画 WebP 等格式需进一步验证具体编码实现，不能因支持静态 WebP 截图就认为支持动画。

## 当前画面与依赖

当前本地依赖为 `@putianyi888/vue3-minesweeper-board@0.6.1` 和 `@putianyi888/vue3-plots@0.6.3`，主线程与 Worker 均使用棋盘库公开接口。

- `BoardPanel.vue` 的 `.video-analyzer-board__main` 内含背景、全局、已打开、概率、鼠标轨迹和光标；控制按钮及进度条位于外侧，应排除。
- 棋盘背景和数字图层使用 vue3-plots 的 ImageGrid canvas，概率、鼠标轨迹也各有 canvas；`BoardCursorLayer.vue` 使用 SVG。只录一个 canvas 会遗漏其他图层和 CSS 不透明度。
- `MinesweeperBoard` 本身仍暴露 cellIndex；0.6.0 的各内置图层公开 render 和 cellSize。Analyzer 从背景层的公开 cellSize 固定实际大小，使用 createBoardRenderer 独立绘制，不读取其私有 canvas。
- 页面 ImageGrid 首次贴图异步加载不再决定导出帧是否就绪；独立 render 的 Promise 等待该输入的贴图解码及画面绘制完成，失败直接拒绝，不用固定延迟掩盖错误。
- 自适应格子大小可能为小数。导出需冻结实际 size；整数像素边界的取整、特定编码器的尺寸限制要在原型中检查，不能偷偷改变格子大小来满足编码器。

## 视频编码

| 方案 | 能力 | 项目取舍 |
| --- | --- | --- |
| Mediabunny | 多容器封装、WebCodecs 编码、显式帧时间、背压、取消、内存或流式输出。 | 首选，不负责 DOM 合成或 GIF。 |
| 原生 MediaRecorder | 录制 MediaStream，按浏览器支持的 MIME 编码。 | 实时捕获可作为兼容候选，不作为准确逐帧导出的主方案。 |
| FFmpeg.wasm | WASM 编解码及封装，不依赖浏览器对同种编码器的原生支持。 | 格式扩展候选；额外下载、CPU、内存和部署要求明显更高。 |

### Mediabunny

npm 调查版本 `1.61.3`，许可证 `MPL-2.0`。官方文档列出的编码器包括 AVC、HEVC、VP8、VP9、AV1；ProRes 的浏览器扩展不能直接视为浏览器编码支持。只有容器支持且当前设备确实可编码的组合才开放，建议优先 MP4 + AVC、WebM + VP9/VP8，其他组合按能力提供。[格式与编码器](https://mediabunny.dev/guide/supported-formats-and-codecs)

`CanvasSource.add(timestamp, duration)` 接受秒单位的显式时间并返回 Promise，可逐帧等待背压；不要求导出处理速度等于成品播放速度。[媒体源](https://mediabunny.dev/guide/media-sources)

`Output.cancel()` 清理编码资源。BufferTarget 保存整个成品；大文件可使用 StreamTarget，但写入必须遵守字节位置，不能随意拼接数据块。流式写入也不自动解决所有浏览器的本地保存能力，取消时不可留下可被误认为完整文件的产物。[写入、取消与目标](https://mediabunny.dev/guide/writing-media-files)

浏览器 WebCodecs 需要相应支持及安全上下文。必须用实际裁剪后的宽高、帧率和质量配置进行能力检测，检测通过后编码仍可能因资源不足失败。[VideoEncoder 能力检测](https://developer.mozilla.org/en-US/docs/Web/API/VideoEncoder/isConfigSupported_static)

### FFmpeg.wasm

包装包 npm 版本 `@ffmpeg/ffmpeg@0.12.15`，许可证为 MIT；WASM core 及其外部编码库的许可证需要分别记录，不能只记包装包。官方示例 core 下载约 31 MB，性能文档说明其开销明显高于原生 FFmpeg，多线程还增加内存需求。[官方示例](https://ffmpegwasm.netlify.app/docs/getting-started/usage/)、[性能](https://ffmpegwasm.netlify.app/docs/performance/)、[FAQ](https://ffmpegwasm.netlify.app/docs/faq/)

建议作为可选扩展动态加载，不默认下载到所有 Analyzer 用户。若采用多线程，应先确认 cross-origin isolation 部署条件；不要为首版导出直接修改全站响应头。官方 core 包含 libwebp，但动画 WebP、AVI 等候选输出仍须核对选定 core 的实际 encoder/muxer 列表并生成文件测试，不在此次调查中承诺支持。[核心库列表](https://ffmpegwasm.netlify.app/docs/overview/)

## GIF 与其他动图

| 库 | 调查结果 | 取舍 |
| --- | --- | --- |
| [gifenc](https://github.com/mattdesl/gifenc) | npm `1.0.3` / MIT。量化、调色板映射、逐帧 writeFrame，可放 Worker；没有内置抖动。 | 适合棋盘平面图形；可释放已处理的 RGBA 帧，但最终编码字节仍积累于内存。需解决发布类型。 |
| [modern-gif](https://github.com/qq15725/modern-gif) | npm `2.1.0` / MIT，内置 TypeScript、Vite Worker 入口、抖动选项。 | 接入较便利，但 Encoder 会保存原始帧直到 flush，必须验证长录像内存及取消释放。 |
| [gif.js](https://github.com/jnordberg/gif.js) | 成熟 Worker 接口、帧延迟及抖动选项。 | 保留候选；更老的打包和 Worker 接线，不优先于前两者。 |
| [UPNG.js](https://github.com/photopea/UPNG.js) | 可编码 APNG，支持全色无损，API 一次接收全部 RGBA 帧。 | 动图扩展候选，不能当作低内存流式编码器；单次播放等控制还需验证。 |

gifenc 的 `v1.0.3/package.json` 没有 types/typings 入口；当前 main 虽有 `types.d.ts`，不能据此认为已发布包类型完整。本次 npm 查询 `@types/gifenc` 返回 404。优先请求上游正确发布声明并验证包，不默认添加本地类型 shim。[发布版本元数据](https://github.com/mattdesl/gifenc/blob/v1.0.3/package.json)

modern-gif 的 `Encoder.encode` 把 RGBA 帧保存在 `_encodingFrames`，`flush` 后才清空；Worker 只是换了存放位置，不消除这部分内存。例：960×512、60 FPS、120 秒，仅原始帧约 13.2 GiB，尚未算量化与成品。这是根据源码和尺寸计算的风险，不是性能实测。[Encoder 源码](https://github.com/qq15725/modern-gif/blob/main/src/Encoder.ts)、[抖动等选项](https://github.com/qq15725/modern-gif/blob/main/src/options.ts)

GIF 的格式约束必须在设置与验收中说明：

- 调色板最多 256 色，透明度只有透明索引，不支持连续 alpha。先按界面效果合成各图层，再量化；半透明轨迹仍可呈现，但不能保证编码后颜色逐像素不变。
- 帧延迟单位为 10 ms。60 FPS 不能每帧固定四舍五入为 20 ms，否则成品明显变慢；应按累计目标时间分配延迟，最终仍受格式精度及播放器行为限制。[GIF89a 规范](https://www.w3.org/Graphics/GIF/spec-gif89a.txt)、[gifenc 延迟编码](https://github.com/mattdesl/gifenc/blob/v1.0.3/src/index.js)
- gifenc 默认 repeat 为 0，即无限循环；本项目应显式设置单次播放，不能沿用库默认值。[gifenc 帧选项](https://github.com/mattdesl/gifenc)
- 可评估连续相同画面合并延迟以减小文件，但属于后续优化，不能改变鼠标轨迹和光标的可见变化。

## 完整画面合成

| 方案 | 优点 | 限制与建议 |
| --- | --- | --- |
| [modern-screenshot](https://github.com/qq15725/modern-screenshot) | npm `4.7.0` / MIT，TypeScript、domToCanvas、可复用 context 与 Worker。 | 第一批原型候选。源码把 canvas 转为图片再复制样式，仍有序列化、图像解码和 foreignObject 开销；不能视为低成本 drawImage。 |
| [SnapDOM](https://github.com/zumerlab/snapdom) | npm `3.3.3` / MIT，可捕获包含样式、字体、图片的 DOM 到 canvas。 | 同列原型候选。每个新时间点需新快照，重复使用同一捕获结果不会反映棋盘变化。 |
| [html-to-image](https://github.com/bubkoo/html-to-image) | 成熟 DOM → SVG foreignObject → canvas 方案，包含 canvas 内容。 | 备选；文档明确提示污染 canvas、大 DOM/data URI 边界。 |
| [html2canvas](https://html2canvas.hertzen.com/documentation) | 根据 DOM/CSS 重建位图。 | 官方说明不是真正截图且不支持所有 CSS；本项目要求效果一致，不作为首选。 |
| 内置层 canvas 合成 + SVG 光标栅格化 | 直接复用现有绘图，可减少每帧 DOM 序列化。 | 技术上可行，但扫描依赖内部 DOM 会耦合实现；应优先请求公开渲染/快照接口，而非复制绘图逻辑。 |

modern-screenshot 的 canvas 克隆包含 `toDataURL()` 及回退像素复制；需确认失败是否会仅警告并留下空层，导出侧不能把缺层当作成功。[canvas 克隆源码](https://github.com/qq15725/modern-screenshot/blob/main/src/clone-canvas.ts)

SnapDOM 官方 GIF/video 插件是实时采集，video 使用 MediaRecorder，文档明确指出慢捕获会拉长时长。它们虽能直接导出文件，但不符合本项目以进度条倍率和显式帧时间保证成品时长的主方案，因此只考虑其单帧捕获能力。[官方插件说明](https://github.com/zumerlab/snapdom/blob/main/packages/plugins/README.md)

## 建议流程与待验证项

当前逐帧流程：冻结页面与设置 → 按输出帧时间定位独立解析副本 → 等待独立 render 完成 → 合成图层并按格子区域裁剪 → 提交编码器 → 释放帧资源 → 完成或取消 → 恢复播放状态。页面位置全程不随导出推进。绘制较慢只延长处理耗时，不能延长成品时长；当前不再安排 Worker 池。

输出时间 `t` 秒对应录像时间 `rangeStartMs + t * playbackRate * 1000`。首次定位必须保留区间起点之前应显示的轨迹；导出不调用普通循环播放来驱动画面。终帧、末帧时长及 GIF 延迟量化需用短片验证，不先随意追加停留帧。

后续验收，不同时安装全部候选库：

1. 验证独立渲染的代表性帧：全部图层、非默认不透明度、SVG 各光标、深浅主题、非整数自适应 size、首见贴图、起点历史拖尾及裁剪边缘。比较页面和未编码帧，分离渲染错误与编码损失。
2. 在相同录像、尺寸、帧率、编码格式和质量下，比较新旧导出耗时并记录渲染与编码占比；源码层面去掉开销不能代替本项目实测。
3. 用 Mediabunny 生成短 MP4/WebM，再按实际可用编码器验证 MOV/MKV/MPEG-TS；核对时长、倍率、首末帧、帧率、尺寸、取消和无编码能力时的错误提示。
4. GIF 比较 gifenc 与 modern-gif，重点检查 60 FPS 延迟累计、单次播放、调色板抖动/闪烁及峰值内存。gifenc 类型缺口解决前不直接加入项目。
5. 更长录像验证背压和内存，不预先保留所有帧；按需评估 FFmpeg.wasm、APNG 和动画 WebP，格式增加必须伴随真实文件验证。

原渲染接口需求已由 0.6.0 满足；若实际验收发现新的依赖问题，继续整理明确的 feature request 并等待更新，不复制库的绘图逻辑。

当前优先级为验证主线程导出画面、成品及清理行为，并测量实际瓶颈；组件测试由用户运行。上面的 GIF 及其他格式仍是候选调查，不是当前已决定同时实施的任务。

不承诺任意格式/尺寸可在全部设备编码，也不承诺 GIF 或有损视频与界面像素完全相同。当前组合及默认值已确定，GIF 等扩展尚未实现。
