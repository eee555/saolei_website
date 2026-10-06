# 项目样式与参数

CSS 与 Less 的选型由实施代理自行决定，根据实际重复程度和维护成本选择；无需逐项征求确认。`src/styles/` 下的文件命名、目录划分和组织方式也由实施代理自行决定。

`src/styles/` 下的项目文件每个不得超过 100 个非空行。空行及仅含空白字符的行不计入，注释行计入；超过时按职责拆分文件，不通过压缩多条声明到同一行规避限制。

`parameters/` 是被 Git 忽略的本地参考存档，不属于项目运行时依赖。应用、组件测试、其他样式及构建脚本均不得直接导入、读取或自动汇总该目录；新检出项目不需要此目录也应能正常构建。

需要参考参数时，将实际需要的值及其依赖变量提取到本目录下对应的样式文件，再使用该文件。例如文字字号放入文字样式文件，按钮尺寸放入按钮样式文件，卡片间距放入卡片样式文件；跨组件共享的颜色可按需建立独立主题文件。具体文件名与 CSS / Less 选型由实施代理决定。

提取后的颜色写入本地色值或引用其他项目变量，不直接读取组件库颜色变量。浅色和深色值一起提取，保留必要的状态、尺寸及局部作用域；新增共享文件通过应用与 Cypress 共用的样式入口接入。

正式项目变量位于 `theme/`，通过 `setup.ts` 加载 `theme/index.css`，应用与 Cypress 组件测试共用。`colors.css` 定义文字、背景、边框与禁用色，`accents.css` 定义主色及状态色，`metrics.css` 定义当前字号、圆角与过渡参数。初值沿用 Element Plus 2.14.6，深色主题继续由 `html.dark` 切换；此批只替换变量来源，不调整尺寸和密度。

项目代码统一使用 `--ui-*`，包括 JavaScript 中的颜色读取。`InputNumber` 的 `--ui-input-*` 与表格的 `--ui-table-*` 支持局部覆盖。组件库要求的 `--el-*` / `--p-*` 声明仅留在 `vendors/` 适配文件，由项目变量向库传值，不反向读取库变量。

`button.css` 保持原有导入路径，按顺序汇总 `buttons/base.css`、`buttons/variants.css`、`buttons/states.css`，分别负责基础布局、类型配色、尺寸与交互状态。

`text.css` 由 `setup.ts` 全局加载，应用与 Cypress 共用。`body` 默认使用项目常规文字色、基础字号和 `overflow-wrap: break-word`，普通文本通过继承获得这些样式；使用 `:where(div, span)` 默认清零 margin / padding，`:where(span)` 默认设置 `vertical-align: middle`，组件自身的样式可覆盖。普通文本无需添加 `.text`；需要覆盖父容器颜色时使用 `.text-regular`，需要不同字号或状态色时保留对应修饰类。已清理可由全局默认覆盖的 `.text` 声明；标题、段落、链接、表单控件及需要固定字号或重置单元格间距的组件仍可使用 `.text`，不删除有实际作用的重置。

`theme/tables.css` 提供三种表格共用的 `--ui-table-*` 参数，由 `setup.ts` 直接加载，应用与 Cypress 共用。初值保持 BaseTable 现有外观：14px 字号、1.4 行高、4px × 8px 单元格内边距、1px 网格边框及 500 表头字重；颜色引用项目主题，随 `html.dark` 切换。

`vendors/element-plus-table.css` 与 `vendors/primevue-table.css` 将同一参数映射到保留的 ElTable / DataTable，并补齐网格线、表头字重和空状态样式。优先使用安装版本的公开变量，必要规则限定在组件内部，不合并组件库分离的表头/正文表格，不改变滚动、固定列、列宽或业务事件。排序箭头、筛选、选择、展开和焦点反馈保留；选中行与普通悬停行使用不同颜色。缓存设置等已有页面局部尺寸覆盖继续优先。

`vendors/primevue-table-controls.css` 仅紧凑化 DataTable 内的分页及展开按钮，并使用项目颜色和直角；不覆盖独立分页器、表单及传送到表外的筛选弹层。复杂行仍由其输入控件和展开内容决定实际高度，不强制所有表格行等高。适配接口参考 [Element Plus Table](https://element-plus.org/en-US/component/table.html) 与 [PrimeVue DataTable](https://primevue.dev/datatable/)，变量名称以项目安装包为准。

`table.css` 是 BaseTable 的共享展示样式，使用项目变量、紧凑单元格与容器内滚动。单元格默认规则通过 `:where()` 降低优先级，便于文字语义类及局部样式覆盖。独立单元格链接与预览，以及调用方已有的原生表头按钮可以保留；例如扫雷榜由页面维护指标选择和后端排序请求，BaseTable 仅提供表头插槽。简单行点击由调用方直接绑定 `<tr>`，同时处理键盘触发及单元格事件冒泡，例如 PB 榜的录像预览；不向 BaseTable 增加行事件接口。依赖组件库内部排序、选择、展开、编辑或复杂联动等能力的表格继续保留现有实现。

正文行悬停时默认使用 `--ui-fill-color-lighter` 高亮单元格，自动适配深浅主题；表头及 `.base-table-empty-row` 空状态行不参与。悬停规则也使用 `:where()`，保留局部特殊单元格背景的优先级。公共样式不设置整行手形光标，有行点击操作时由调用方自行设置。

`table-columns.css` 提供按列内容复用的公共类，BaseTable 通过 `@/styles/` 别名依次直接导入它和 `table.css`，避免此处相对 CSS `@import` 被 PostCSS 解析到项目根目录。使用 BaseTable 时自动加载。目前密度榜、扫雷榜和 PB 榜共用这些规则，避免页面重复写对齐、宽度或 `nth-child()` 列序号选择器。

| 类名 | 适用列 | 默认样式 |
| --- | --- | --- |
| `table-col-rank` | 排名、序号 | 宽度、最小宽度及最大宽度均为 4em、居中、不换行 |
| `table-col-player` | PlayerName、玩家名 | 最小宽度 150px、左对齐 |
| `table-col-number` | Time、Bvs、STNB、3BV、Pluck 等数值 | 最小宽度 100px、右对齐、不换行、等宽数字 |
| `table-col-datetime` | 上传时间等日期时间 | 最小宽度 170px、居中、不换行 |
| `table-col-center` | 模式、分组表头等 | 居中，不规定宽度 |

在对应的原生 `<th>` 和 `<td>` 上使用同一个类，例如 `<th class="table-col-number">Bvs</th>` 与 `<td class="table-col-number">{{ value }}</td>`。这些类只定义外观，不负责计算排名、数值格式化或渲染 PlayerName，也不需要新增列组件。最小宽度由公共文件统一维护，玩家、数值和日期时间列可随内容与容器增长；特殊表格按需要局部覆盖，不通过列的位置推断语义。保留组件库的表格后续按其样式接口单独接入。

按实际使用范围小步提取，不整体搬入组件库参数，也不建立依赖本地存档的统一入口。实施进度见[前端 UI 重构计划](../../UI_REFACTOR_PLAN.md)。
