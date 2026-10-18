# Feature Request: MouseTrace 支持可配置线型

## 状态

2026-10-12：中文需求草稿，未提交。已核对当前安装的 minesweeper-board 0.6.1 的 MouseTrace 声明：支持 lineWidth 和四种按键状态的 color，没有虚线、点线、端帽和连接样式 props。Analyzer 已接入现有线宽、线色及完整 marker 设置，不阻塞这些功能。

## 场景

录像分析页面允许用户调整轨迹样式；线型应由棋盘依赖统一渲染，页面、独立 render 和后续 Worker 输出保持一致，不由调用方另外绘制轨迹。

## 请求

- 可设置虚线序列和偏移，例如 lineDash: number[] 与 lineDashOffset: number，单位为格，按实际 cellSize 缩放。空数组保持现有实线；可通过序列实现虚线、点线等，不要求库维护命名预设。
- 可设置 lineCap（butt/round/square）及 lineJoin（round/bevel/miter），默认保持当前 round 行为。
- 默认值兼容现有画面；非法、非有限或负的虚线长度要有明确处理约定，不能产生静默缺层或未处理异常。
- 明确虚线相位在相邻事件段、按键状态换色和拖尾左端点移动时的规则，增量绘制与完整重绘必须一致；建议沿连续轨迹累计相位，换色不重置。
- 同步 MouseTrace props、公开 TypeScript 类型、独立渲染的 MouseTraceSettings 和 Worker 绘图实现；不只提供 CSS（Canvas 线条不受 CSS 线型影响）。
- 不要求改变 marker 样式、事件数据、时间定位或应用设置 UI，调用方负责预设、控件及 localStorage。

## 验收

1. 实线、虚线及点线在不同和非整数格子大小下对齐；默认输入与旧版本效果一致。
2. 跳转、回退、拖尾平移及增量追加事件后无旧线条残留，相同范围的完整重绘结果一致。
3. 按键状态换色和同时间戳多段轨迹保持约定的相位；marker 独立生效。
4. 同一输入的 Vue 组件、独立 render 和 Worker 输出保持同一视觉语义，声明与文档同步。
