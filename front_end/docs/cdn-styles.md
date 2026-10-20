# 公共样式 CDN 与本站回退

网站构建将 Element Plus 的基础 CSS、PrimeIcons CSS 和图标字体交给 jsDelivr。JS 保持现有 Vite 按需打包，Element Plus 暗黑变量和本站覆盖样式仍由本站加载。

## 行为

- 构建从已安装 npm 包读取版本，CDN URL 固定版本；同一次构建将原始 CSS、PrimeIcons 字体复制到 `assets/vendor/<包名>-<版本>/`。不需要单独上传资源，也不在构建时访问 CDN。
- HTML 内的小脚本立即发起两份样式请求，与应用模块并行下载。加载界面使用内联样式，不等待 CDN。
- 加载页以中英文显示 CDN 加载、超时或失败后的本站回退、资源就绪等状态。进度条累计两份 CSS 和一份字体，显示“界面资源 0/3”到“3/3”；回退请求不重复计数。该计数仅覆盖这三项界面资源，不代表 JS、路由或整页下载百分比。
- CDN 请求失败立即回退本站；CSS 和字体合计超过 4 秒也回退。PrimeIcons 通过浏览器的 Font Loading API 检测字体，处理 CSS 成功、字体失败的情况。
- 每份样式独立回退，正常情况下不请求本站副本；切换时移除原 CDN 样式，在原位置插入本站样式，保持主题覆盖顺序。
- 首次挂载同时等待路由与样式准备完成。本站样式和字体也失败或超过 15 秒时，保留加载界面并显示现有“页面加载失败，请刷新重试”提示。
- 本站 CSS 副本进入现有 gzip 流程。发布时需要完整部署 `dist`，包括 `assets/vendor`，并保留旧版本资源以支持尚未刷新的页面。
- Vite 开发、Cypress 组件测试、离线分析器使用原有本地导入，不依赖 CDN。

## 验证与关闭

执行 `npm run build:openms` 构建，部署后在浏览器禁用缓存检查：

1. 正常访问：样式和 PrimeIcons 字体来自 `cdn.jsdelivr.net`，不请求 `assets/vendor`。
2. 在开发者工具中阻止 `*cdn.jsdelivr.net*`：两份样式回退本站，页面和图标正常。
3. 仅阻止 `*cdn.jsdelivr.net/npm/primeicons@*/fonts/*`：Element Plus 继续使用 CDN，PrimeIcons 样式及字体回退本站。
4. 模拟 CDN 请求一直不返回：约 4 秒后发起本站请求；切换后主题、按钮、弹窗与图标仍正常。
5. 同时阻止 CDN 和 `*/assets/vendor/*`：显示加载失败，避免挂载缺少样式的页面。

超时不等同于整页最多等待 4 秒；回退后的本地下载仍取决于服务器带宽。可在构建环境设置 `VITE_CDN_STYLES=false` 关闭此功能，恢复全部由 Vite 打包；该设置只在重新构建后生效。

## 方案依据

调查了项目现有导入和 [vite-plugin-cdn-import](https://github.com/mmf-fe/vite-plugin-cdn-import)。该插件面向 JS 全局变量替换；其文档没有覆盖此次需要的样式超时、字体检测和本站副本处理，因此本项目使用 Vite 官方插件接口与浏览器原生资源事件，不新增运行时依赖。

- [Element Plus 官方 CDN 引入](https://element-plus.org/zh-CN/guide/installation#浏览器直接引入)：采用其固定版本的 jsDelivr CSS 地址。
- [Vite Plugin API](https://vite.dev/guide/api-plugin)：使用 `resolveId`、`emitFile` 和 `transformIndexHtml`，保留共享源码中的原始 CSS 导入供开发与离线构建使用。
- [FontFaceSet.load](https://developer.mozilla.org/en-US/docs/Web/API/FontFaceSet/load)：确认图标字体可用后才结束加载阶段。

其他 JS 包继续保留按需裁剪；旗帜样式已随下载说明按需加载，本次不提前引入，避免扩大首屏下载范围。
