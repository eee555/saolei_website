# Analyzer 更新记录 / Analyzer changelog

## 0.1.3 — 2026-10-18

- 修复图层开关及显示设置触发全部计数器和自定义事件重新采样造成的卡顿；保留无关配置更新时的采样缓存。
- Fix stalls when toggling layers or changing display settings by retaining counter and custom-event samples across unrelated configuration changes.

## 0.1.2 — 2026-10-13

- 离线页面的信息区和浏览器标签页采用定制 Analyzer 图标，SVG 内联到 HTML，断网打开时无需外部图标文件。网站录像页的离线包下载按钮使用同一图标。
- Use the custom Analyzer icon in the offline info area and browser tab, inlined into the HTML for offline use. The website replay page uses the same icon for the offline package download button.

## 0.1.1 — 2026-10-13

- 离线包统一命名为 `OpenMinesweeperVideoAnalyzer-版本号.zip`，网站下载链接和保存文件名同步使用独立版本。
- Name offline archives `OpenMinesweeperVideoAnalyzer-version.zip`; the website download URL and filename use the same independent version.

## 0.1.0 — 2026-10-13

- 建立 Analyzer 独立版本基线；离线信息区显示版本，ZIP 附带同源版本文件。
- 包含现有本地录像解析、棋盘/计数器/plot、视频导出、中英文切换及包内帮助与许可声明。

- Establish an independent Analyzer version; display it in the offline info area and include the same version file in the ZIP.
- Includes local replay analysis, board/counters/plots, video export, language switching, and bundled help and license notices.
