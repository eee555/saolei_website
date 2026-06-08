# VideoScatter 组件架构

`VideoScatter` 是一个以 `App.vue` 为入口的视频散点图组件。它负责接收外部传入的视频摘要数据，提供坐标轴、点样式和选择模式配置，并在画布中渲染可交互的散点图。

## 文件结构

```text
VideoScatter/
├── App.vue      # 入口组件，组装工具栏和画布
├── Toolbar.vue  # 控制面板，修改散点图配置和选择模式
├── Canvas.vue   # 绘图区域，渲染散点图并处理鼠标交互
├── store.ts     # Pinia 状态仓库，维护原始数据、选择状态和派生散点数据
└── utils.ts     # 数据转换工具
```

## 入口组件：App.vue

`App.vue` 是组件的对外入口，职责保持得很薄：

- 接收 `videos` prop，类型为 `VideoAbstract[]`。
- 监听 `videos` 变化，并调用 `VideoScatterStore.setRawData` 同步到 store。
- 在模板中按上下布局渲染 `Toolbar` 和 `Canvas`。

整体结构如下：

```text
App.vue
└── .video-scatter
    ├── Toolbar.vue
    └── Canvas.vue
```

这意味着父组件只需要把视频数据传给 `App.vue`，后续的配置、渲染和选择状态都由 `VideoScatter` 内部模块协作完成。

## 状态层：store.ts

`store.ts` 定义 `VideoScatterStore`，是组件内部的数据中心。

核心状态包括：

- `rawData`：外部传入的原始视频数组。
- `canvasMode`：画布模式，当前支持普通光标模式和 `select` 选择模式。
- `selectionMode`：框选后的选择合并策略，支持 `assign`、`union`、`diff`、`intersect`。
- `selectedFlags`：与 `rawData` 下标对应的布尔数组，表示每个视频是否被选中。

核心 getter：

- `scatterData`：根据当前 `VideoScatterConfig` 把 `rawData` 转换成绘图所需的 `indices`、`points` 和 `colors`。

核心 action：

- `setRawData(data)`：更新原始数据，并重置选择状态。
- `selectionDraw(shape)`：根据当前选择模式，把画布上的选择区域应用到 `selectedFlags`。

`scatterData` 同时依赖全局配置 `VideoScatterConfig` 和颜色主题 `colorTheme`，因此坐标轴、颜色字段、点半径、是否只显示选中项等配置变化后，画布会通过响应式数据自动更新。

## 工具栏：Toolbar.vue

`Toolbar.vue` 负责提供用户可操作的配置入口，主要修改两类状态：

- 修改 `VideoScatterConfig`：
  - `x` / `y`：选择散点图横纵轴对应的统计字段。
  - `radius`：调整散点半径。
  - `showOnlySelected`：只显示已选中的点。
  - `highlightSelected`：高亮已选中的点。

- 修改 `VideoScatterStore`：
  - `canvasMode`：切换普通光标或框选模式。
  - `selectionMode`：在框选模式下选择赋值、并集、差集或交集策略。

因此，`Toolbar` 不直接绘图，也不直接处理数据转换；它只修改配置和交互状态。

## 画布：Canvas.vue

`Canvas.vue` 是散点图的渲染和交互层。

它组合了 `Plots` 模块中的多个绘图组件：

- `Grid`：绘制背景网格。
- `Scatter`：绘制散点，并绑定点击、悬停事件。
- `Axes`：绘制坐标轴和坐标轴标签。
- `MouseDraw`：在选择模式下接收鼠标绘制区域。

主要职责包括：

- 从 `VideoScatterStore.scatterData` 读取点和颜色。
- 根据点数据计算 `domain`、`xTicks` 和 `yTicks`。
- 使用 `ResizeObserver` 监听容器尺寸变化，动态更新绘图尺寸。
- 鼠标悬停点时，通过 `Tippy` 和 `VideoAbstractDisplay` 显示视频摘要信息。
- 点击点时调用 `preview(point.data.id)` 预览视频。
- 框选完成后，将 SVG 坐标下的选择形状转换为数据坐标，再交给 `VideoScatterStore.selectionDraw` 更新选择状态。

## 数据流

```text
父组件传入 videos
        │
        ▼
App.vue watch(videos)
        │
        ▼
VideoScatterStore.setRawData
        │
        ▼
VideoScatterStore.scatterData
        │
        ├── 读取 VideoScatterConfig 的 x / y / colorBy / showOnlySelected
        ├── 使用 utils.videoToPlotPoint 转换视频为散点坐标
        └── 根据 colorTheme 计算每个点的颜色
        │
        ▼
Canvas.vue 渲染 Grid / Scatter / Axes / MouseDraw
```

用户交互的反向数据流：

```text
Toolbar 修改配置或模式
        │
        ├── VideoScatterConfig 变化后触发 scatterData 重新计算
        └── VideoScatterStore.canvasMode / selectionMode 影响 Canvas 交互

Canvas 框选区域
        │
        ▼
shapeToData 转换到数据坐标
        │
        ▼
VideoScatterStore.selectionDraw
        │
        ▼
selectedFlags 更新
        │
        ▼
scatterData 根据 showOnlySelected 等配置重新派生
```

## 工具函数：utils.ts

`utils.ts` 当前提供 `videoToPlotPoint(video, statX, statY)`：

- 从 `VideoAbstract` 中读取指定的 x/y 统计字段。
- 返回携带原始 `video` 数据的 `PlotPoint<VideoAbstract>`。
- 当 x 或 y 不是有限数值时返回 `undefined`，避免无效点进入绘图层。

## 组件边界

- `App.vue`：对外入口和模块组装。
- `Toolbar.vue`：只负责用户配置输入。
- `Canvas.vue`：只负责绘图、尺寸监听和图形交互。
- `store.ts`：负责原始数据、选择状态和绘图数据派生。
- `utils.ts`：负责可复用的数据转换逻辑。

这种拆分让入口组件保持简单，也让配置、状态、渲染和数据转换各自有清晰边界。
