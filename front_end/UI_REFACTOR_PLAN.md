# 前端 UI 风格渐进重构计划

制定日期：2026-10-03。现状核查与整理：2026-10-07。

本计划以当前代码为实施起点，只列剩余工作和持续适用的约束。按用户约定，已提交或明确验收的改动不再列为实施或测试待办。普通页面描述布局、周赛报名表和 Checkbox 4.1.1 均已提交；图标迁移 7.1、Checkbox 4.1.2 / 4.1.3 已验收；图标迁移剩余 7.2，Checkbox 4.1.4 已实施，待验收。批次编号保留，避免后续交流中混淆。

## 目标与固定约束

- 面向数据展示与分析，以直角、紧凑布局和清晰对齐为主，优先减少多余间距，不以普遍缩小字号代替密度改善。
- 同时支持浅色与深色主题。主要配色沿用已提取的 Element Plus 基准值，应用代码使用项目 `--ui-*`，不直接读取组件库颜色变量。
- 组件根据自身可用宽度伸缩、换行或内部滚动；少数确需切换布局的组件单独制定策略，不设置全站宽窄屏布局分界。
- 简单布局和展示采用原生 HTML + CSS，复用项目已有基础组件。复杂交互保留现有组件逻辑，主要调整样式。
- vue-tippy 保持现有实现及样式导入方式。PrimeVue 按项目既定决定逐步退出，PrimeIcons 单独保留。
- 禁止全局注册全量 Element Plus 图标；过渡期仅注册实际依赖全局解析的图标，最终不全局注册任何图标。图标选型继续优先 PrimeIcons，其次 Element Plus。
- 每批围绕一个可独立审查、合并和回退的结果，避免与业务逻辑修改、文件搬迁或整页重写混在一起。

新增 UI 和业务维护优先遵守[根目录前端规范](../.codex/instructions.md)。管理员页面只承接必要的功能与主题兼容，不安排专门的精细视觉改版。

## 当前可复用的基础

以下能力已经落地，后续直接复用，不重新建立同类基础设施。

| 基础 | 当前实现与维护入口 |
| --- | --- |
| 主题与参数 | [`theme/`](src/styles/theme/) 提供独立颜色、字号、圆角、过渡和表格参数；[`setup.ts`](src/setup.ts) 为应用与 Cypress 加载主题和库适配 |
| 全局文字 | [`text.css`](src/styles/text.css) 设置 body 常规文字色、基础字号和换行方式；div / span 默认零 margin、零 padding，span 默认行内居中 |
| 文字语义 | 普通文本可继承默认样式；需要独立常规文字色时使用 `text-regular`，保留字号与状态色修饰类；标题、链接、控件等仍可使用有实际重置作用的 `text` |
| 有色数据单元格 | [`PiecewiseColorScheme`](src/utils/colors.ts) 按背景明暗引用浅色 / 深色模式的默认文字色；透明背景继承父容器颜色。两套来源为 `--ui-text-color-regular-light` / `--ui-text-color-regular-dark` |
| 布局、卡片与操作 | `layout.css`、`cards.css`、`link.css`、`button.css` / `buttons/`；`BaseButton`、`BaseTextButton`、确认/取消按钮、`BaseFileInput` 等已有原生实现 |
| 描述列表 | [`descriptions.css`](src/styles/descriptions.css) 提供 dl / dt / dd 模板，支持边框、跨列和容器宽度适配，无独立 Vue 组件；普通页面已验收 |
| 展示表格 | [`BaseTable`](src/components/common/BaseTable.vue) 封装原生表格、滚动容器、空状态和插槽；`table.css` 提供行悬停高亮，`table-columns.css` 提供排名、玩家、数值、时间等公共列样式 |
| 保留表格的视觉 | `theme/tables.css` 为 BaseTable、ElTable、PrimeVue DataTable 提供统一参数；`vendors/element-plus-table.css`、`primevue-table.css`、`primevue-table-controls.css` 已接入 |
| Element Plus 按钮兼容 | `vendors/element-plus.css` 已提供直角覆盖；暂留组件继续使用，不重复安排按钮整体迁移 |
| 图标注册 | [`main.ts`](src/main.ts) 仅显式全局注册实际使用的 14 个图标；组件测试按挂载链分别注册，不在 Cypress 公共入口注入图标；7.1 已验收 |
| 原生 Checkbox | [`checkbox.css`](src/styles/checkbox.css) 与 [`checkbox-buttons.css`](src/styles/checkbox-buttons.css) 由 setup.ts 为应用与 Cypress 加载；原生 input / label + 共用 class，提供直角、主题、选中、悬停、键盘焦点和禁用样式，支持数组多选与按钮外观，无 BaseCheckbox 组件 |

已迁移的表格包括密度榜、扫雷榜、PB 榜、比赛积分榜、软件版本列表、个人纪录、自定义计数器和周赛报名表。比赛积分榜由页面管理后端排序，切换字段重置页码，表头不显示排序箭头。

目前的尺寸是后续评审的起点：基础文字 14px，普通原生按钮内边距 4px × 8px、行高 1.4；表格单元格内边距 4px × 8px、行高 1.4；普通卡片内边距 10px。这些现值已生效，后续按组件类别调整，不再安排“先抄参数但不接入运行时”的步骤。

## 剩余工作与建议顺序

| 批次 | 工作 | 范围与边界 |
| --- | --- | --- |
| 2 | 剩余描述布局 | 剩余 10 个文件共 11 处 ElDescriptions 位于管理员与账号关联区域，按既定范围暂缓 |
| 3 | 剩余表格核对 | 其余 5 个 ElTable 根据实际排序、编辑等依赖决定是否保留 |
| 7 | 图标注册迁移 | 剩余 7.2：逐模块取消全局图标注册，同步处理 Cypress 注册 |
| 4 | 简单选择控件迁移与复杂组件换肤 | 先按 4.1 迁移 Checkbox；其余输入与表单、选择控件、Tabs、菜单、弹窗、通知和加载状态各自独立成批 |
| 5 | PrimeVue 退出 | 筛选控件、表格替代验证、逐表迁移和依赖清理；随相关模块维护推进 |
| 6 | 局部收尾 | 随每批删除失效导入、重复样式和已无使用方的兼容项，更新本计划 |

下一步验收 4.1.4 的上传表格半选与遗留调用收尾，再按 4.2 逐类处理其他控件；7.2 可独立合并。批次 4 的其他换肤不需要等待全部简单组件迁移完毕。首页比赛卡片、账号关联页面重做和 PrimeVue 全部退出不作为其他批次的前置条件。

### 2. 剩余描述布局

剩余 11 处 ElDescriptions 位于 10 个文件，按既定范围暂缓：

- 管理员区域 4 处：`components/GSCAdmin/GeneralInfo.vue`、`views/StaffView/Task.vue`、`VideoModel.vue`、`WeeklyTournament.vue`，随维护迁移；保留动态循环、v-loading 和条件显示。
- 账号关联区域 7 处：`CardMineracer.vue`、`CardBilibili.vue`、`CardAddMineracer.vue`、`CardWoM.vue`（2 处）、`CardSaolei.vue`、`CardMsgames.vue`，随页面重做处理。

后续直接复用模板，按实际列数与跨列需求完善局部 CSS；不复制 ElDescriptions 的完整 API，也不将子控件的交互重写纳入布局迁移。

### 3. 剩余展示表格

BaseTable 的迁移边界保持如下：

- 单元格可包含玩家链接、录像预览、下载、按钮和其他独立操作。
- 页面已有的后端排序状态与请求，可由原生表头按钮配合表头插槽承接；后端分页本身不构成保留 ElTable 的理由。
- 简单行点击可由调用方绑定 `tr`，调用方负责键盘触发及独立单元格操作的事件冒泡。
- BaseTable 不新增内部排序、筛选、选择、展开、编辑、分页或递归列注册体系。分组表头直接使用原生 rowspan / colspan。

当前仍有 5 个 ElTable 使用方：

| 使用方 | 当前判断 |
| --- | --- |
| [`widgets/IdentifierManager.vue`](src/components/widgets/IdentifierManager.vue) | 使用内部排序及单元格编辑，暂留 |
| [`gsc/AllSummary.vue`](src/views/TournamentView/gsc/AllSummary.vue) | 使用内部客户端排序，暂留 |
| [`weekly/AllSummary.vue`](src/views/TournamentView/weekly/AllSummary.vue) | 使用内部排序及自定义比较函数，暂留 |
| [`TournamentList.vue`](src/views/TournamentView/TournamentList.vue) | 使用默认排序和可排序列，暂留；保留原因包含排序，简单行点击本身不是障碍 |
| [`VideoView.vue`](src/views/VideoView.vue) | 使用库排序事件、列状态与固定列，另行核对迁移成本；本批先保留 |

其余表格继续使用已统一的视觉样式，不在本批顺带重写内部排序或编辑逻辑。未来按实际使用能力重新评估，而不以表格名称或是否包含按钮作决定。

### 7. 剩余图标注册迁移

7.1 已验收，应用全局注册已收缩为实际使用的图标，以下仅保留 7.2 所需的依赖清单与迁移安排。最终应用与组件测试都不全局注册任何图标。继续保留组件库内部自行导入的图标，不要求移除 `@element-plus/icons-vue` 依赖，也不将 PrimeIcons 的 CSS 类用法视为 Vue 全局组件注册。

当前入口及依赖已核对：

- [`main.ts`](src/main.ts) 显式导入 14 个图标，通过有限映射调用 `app.component`；已删除全库命名空间导入和枚举。
- [`Menu.cy.ts`](src/views/Menu.cy.ts) 在 `global.components` 中注册菜单及登录弹窗渲染链需要的 10 个图标；Cypress 组件挂载不执行 main.ts，测试注册单独维护。
- [`IconMenuItem.vue`](src/components/widgets/IconMenuItem.vue) 通过 `<component :is="props.icon">` 解析菜单传入的字符串；菜单数据、`prefix-icon` 等字符串 props 也需检查，不能只搜索图标标签。
- 已核对当前安装包：ElMenu 子菜单箭头直接导入 `ArrowDown` / `ArrowRight`；ElFormItem 相关状态图标由 ElInput 的校验状态映射承接，加载、成功、失败及密码显隐图标已在库内部导入。这些内部使用本身不要求项目全局注册；`prefix-icon="User"` 等项目传入的字符串仍需全局解析。

7.2 需要逐模块消除的全局依赖如下，去重后共 14 个；历史注释与 ESLint ignorePatterns 不作为实际使用依据：

| 调用来源 | 图标 |
| --- | --- |
| `views/Menu.vue` 配置与固定菜单项，经 `widgets/IconMenuItem.vue` 动态解析 | Trophy、VideoCameraFilled、Medal、Cpu、User、Key、Reading、Setting |
| `Login/LoginForm.vue`、`Login/RegisterForm.vue`、`formItems/EmailFormItem.vue`、`EmailCodeBlock.vue`、`PasswordConfirmBlock.vue` 的输入前缀；找回密码表单复用后面三个组件 | User、Lock、Key、Message |
| `visualization/ColorSchemeSetting.vue`、`accountlinks/CardWoM.vue`、`widgets/UserArbiterCSV.vue` 的裸标签 | ArrowLeft、ArrowRight、Ticket、QuestionFilled |

7.2 需要同步移除的测试注册如下：

| 测试 | 注册图标 |
| --- | --- |
| `views/Menu.cy.ts` | 菜单的 8 个图标，以及登录、注册、找回密码弹窗需要的 Lock、Message，共 10 个 |
| `Login/LoginForm.cy.ts` / `Login/RegisterForm.cy.ts` | Key、Lock、User / Key、Lock、Message、User |
| `formItems/EmailCodeBlock.cy.ts` / `PasswordConfirmBlock.cy.ts` | Key / Lock |
| `accountlinks/CardWoM.cy.ts` / `App.cy.ts` | Ticket；现有 `mountAccountLink` 允许调用方传入有限的组件映射，其他账号关联测试默认不注册图标 |
| `VideoPlayer/NativePlayer.cy.ts` / `views/UserView/UserVideoView.cy.ts` | ArrowLeft、ArrowRight / QuestionFilled |

#### 7.2 后续目标：不全局注册任何图标

按菜单、表单、其他裸标签分别迁移。优先复用现有 BaseIcon / PrimeIcons；需要 Element Plus 图标时在使用方按名称局部导入。IconMenuItem 使用组件对象或封闭的局部映射解析现有字符串，图标 props 改为显式组件绑定，消除全局名称解析。只改变图标依赖，保留尺寸、提示、语义与业务事件。

每完成一个模块，移除对应全局注册及不再需要的测试注册、ESLint 图标名称豁免。菜单动态解析可能没有未解析组件警告，需实际确认 SVG / 项目图标存在及布局未退化。最后删除应用的图标注册映射与注册循环，组件测试也不再用 `global.components` 注入图标；以源码检查及实际渲染验收确认全局图标注册归零。

### 4. 简单选择控件迁移与复杂组件换肤

#### 4.1 Checkbox 迁移收尾（4.1.4 已实施，待验收）

2026-10-07 核对：4.1.1 已提交，4.1.2 / 4.1.3 已验收；4.1.4 已迁移上传表头 / 行选择和关闭通知分支，删除 ElCheckbox 与 CheckboxValueType 导入。应用源码中 ElCheckbox、ElCheckboxGroup、ElCheckboxButton 调用已归零；组件库内部自带的 checkbox 不在本次直接替换范围内。

采用原生 `<input type="checkbox">`、关联 label 与共用 CSS class，跳过 BaseCheckbox 组件。布尔和数组模型复用 Vue 原生 `v-model`；样式通过 `:checked`、`:indeterminate`、`:focus-visible`、`:disabled` 等原生状态选择器复用，不用业务代码维护重复的状态 class。按钮外观采用同一控件的样式变体。半选属性和上传全选策略由 Table.vue 局部同步，不另建通用 Checkbox 状态层。

普通用法模板如下，具体样式文件按实施需要组织：

```vue
<label class="checkbox">
    <input v-model="checked" class="checkbox-input" type="checkbox">
    <span>选项文本</span>
</label>
```

保留已有业务 class 和事件。原生 `change` 的参数是 DOM Event，涉及原 ElCheckbox 布尔回调的调用点应显式读取 input.checked；已有业务组件对外的 change 值与触发次数继续保持原来的契约。

| 调用方（均相对 src） | 模型与作用 | 保留事项与判断 |
| --- | --- | --- |
| [`App.vue`](src/App.vue) | `never_show_notice`：不再显示通知，1 处 | 已迁移，待验收；所属 ElDialog 仍为 `v-if="false"`，不启用通知、不改存储逻辑 |
| [`components/VideoUpload/Table.vue`](src/components/VideoUpload/Table.vue) | 表头全选 / 半选与各行布尔选择，2 处 | 已迁移，待验收；原生 change 承接操作，半选用 DOM property，选中行与筛选联动保持原实现；表头及各行提供本地化可访问名称 |

三状态的迁移判断：

- 上传表头的半选是由 `selectedRows` 派生的状态，模型本身仍是选中行数组。原生 checkbox 支持独立于 checked 的 `HTMLInputElement.indeterminate` 属性，通过 DOM property 同步即可；不能仅添加同名 HTML attribute，也不需要引入三值循环控件。参见 [MDN 半选状态](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/checkbox#indeterminate_state_checkboxes)。
- 必须保留现有表头规则：未选时选择全部 `filteredData`（包括其他分页中的过滤结果），半选或全选时清空。筛选变化后剔除已不在结果中的选择；空结果显示未选。`VideoUpload/App.cy.ts` 已验证半选点击清空，不能改成常见的半选点击全选。
- 原生激活会翻转 checked 并清除 indeterminate，迁移时需按最终选中行重新同步二者；半选清空时，即使派生 checked 前后都是 false，也必须保证 DOM 最终未选。点击标签与输入框、以及 Space 都只执行一次选择操作。参见 [HTML checkbox 激活规则](https://html.spec.whatwg.org/multipage/input.html#checkbox-state-(type=checkbox))。

剩余子批次如下，实施后单独验收：

| 子批次 | 范围 | 实施边界 |
| --- | --- | --- |
| 4.1.4 | 上传表格半选与遗留调用收尾（已实施，待验收） | Table.vue 局部同步原生 indeterminate 与 checked；共用 CSS 已补齐半选外观，同步关闭通知分支，清理失效导入及 CheckboxValueType。PrimeVue 的筛选、排序、分页与展开继续保留 |

Checkbox 样式采用项目主题参数，覆盖直角、紧凑尺寸、checked、indeterminate、hover、focus-visible 和 disabled；保留原生输入的焦点、Space 和可访问名称。CSS / Less 与文件组织按既定规则自行决定，每个正式样式文件不超过 100 个非空行。

4.1.4 测试同步范围：`VideoUpload/App.cy.ts` 与 `cypress/e2e/profile.cy.ts` 已改用原生输入查询；现有 `cy.shouldHaveState()` 改为可重试的 checked / indeterminate 属性断言，以 null 表示半选。上传组件测试保留全部状态序列，补充标签点击与 Space；新增 `VideoUpload/Table.cy.ts` 验证跨页全选、半选清空、筛选后剔除选择、空结果以及空结果点击后的 DOM 状态。关闭的通知分支不新增完整页面测试。

已验收的数组多选与按钮外观继续复用 checkbox.css / checkbox-buttons.css，具体模板与尺寸见样式 README。筛选组件保持先更新模型、等待 nextTick 后发出一次数组 change 的契约；外部模型更新不触发 change。ESLint 已将 ElCheckbox、ElCheckboxGroup、ElCheckboxButton 限制并入公共规则，所有参与 lint 的 Vue 文件禁止新增这些组件，不扩展原有整文件忽略范围。

4.1.4 的 `lintfix`、`typecheck`、`build:frontend` 与 `git diff --check` 均通过；checkbox.css 为 82 个非空行。代理未运行 Cypress，由用户在 `front_end` 运行：

```powershell
npx.cmd cypress run --component --spec "src/components/VideoUpload/Table.cy.ts,src/components/VideoUpload/App.cy.ts"
npx.cmd cypress run --e2e --browser chrome --spec "cypress/e2e/profile.cy.ts"
```

浏览器验收重点为深浅主题下的半选横线、全选 / 清空、方框与 label 点击、Tab / Space、焦点可见、筛选与分页后的状态及原有上传操作；静态检查不代表这些行为已在浏览器验证。

#### 4.2 其他复杂组件换肤与尺寸细化

表格共用视觉和按钮直角适配已经完成。本阶段处理尚未统一的类别，每类先选择一个代表实例验证，再推广：

| 子批次 | 代表实例 | 重点 |
| --- | --- | --- |
| 输入与表单 | 登录/注册、EditProfile、播放器设置 | 输入高度、内边距、圆角、标签与校验间距；保留输入、焦点及校验行为 |
| 选择控件 | 排行榜或设置页的 Select、Radio、Switch、Slider | 控件与下拉浮层尺寸、选中/禁用/焦点状态，保留单选、多选和数值范围语义；Checkbox 按 4.1 单独迁移 |
| Tabs | 首页或用户页面 | 标签高度、内容间距、边框和激活状态，保留标签切换与路由状态 |
| 菜单 | `views/Menu.vue` | 单独处理菜单项间距和主题；保留用户可配置的高度、字号、图标模式与导航 |
| 弹窗、通知与加载 | BaseOverlay、登录弹窗、Notifications、v-loading | 内部间距、边角、按钮区域和浮层；保留关闭、滚动、焦点、遮罩和加载行为 |

按实际需要提取控件高度、间距、行高等项目参数，同时覆盖正常、悬停、焦点、禁用、加载、错误和空状态。不要只将所有控件切为 `small`，也不要直接将所有字号或全局圆角统一缩小来代替逐类检查。

保留主题切换机制。下拉框、弹窗和通知可能挂载到 body，使用组件公开的浮层 class / 样式接口接入，不能只依赖业务页面的 scoped CSS。现有 App.vue 中的浮层层级修复继续保留，确需迁移时单独验证。

### 5. PrimeVue 退出

不新增 PrimeVue 使用范围。当前依赖仍包含以下内容，表内分页器之外的实际行为也必须保留：

| 依赖 | 当前使用方 |
| --- | --- |
| DataTable / Column | `components/VideoList/App.vue`、`components/VideoUpload/Table.vue`、`components/accountlinks/VideoImportQueue.vue`、`views/StaffView/AccountLink.vue`、`views/StaffView/Task.vue`，共 5 个表格入口；VideoList 下还有复用列组件 |
| Listbox | VideoList 的模式、软件、状态、难度列，以及上传表格、录像导入队列的筛选器 |
| Select | `views/StaffView/Task.vue` 的状态筛选器 |
| Toolbar | 6 个账号关联卡片及 `views/StaffView/Task.vue`，共 7 处 |
| 注册、主题与类型 | main.ts 中 PrimeVue / Aura preset，`@primevue/core/api`、DataTable 事件类型及相关 Cypress 测试的注册 |

按以下小步骤推进：

1. 随模块维护逐个替换外围筛选控件，保留值类型、单选/多选、筛选回调和筛选清空语义；优先复用已有控件，不同时重写表格状态。
2. 单独验证表格与分页的替代组合。先核对项目现有 Element Plus 表格与分页组件能否满足需求，验证完成后再决定实现，不预先迁移全部表格。
3. 选择交互较少的表格试点，再逐表替换；每个表格单独核对排序、筛选、分页、展开、选择及行操作的处理顺序和语义。
4. Toolbar 随账号关联页面重做或管理员任务页维护处理；新布局采用原生容器与 CSS，不为旧页面复制整套 Toolbar API。
5. 最后一个使用方退出后，再清理注册、preset、过渡样式、测试配置以及 `primevue`、`@primevue/core`、`@primeuix/themes` 依赖和锁文件。PrimeIcons 保留。

现有 `vendors/primevue-table*.css` 已完成必要的表格过渡适配，不再重复安排建立这些文件，也不建设完整的 PrimeVue 主题体系。是否提取 main.ts 中的 preset，按实际维护需要决定。

分页替代验证至少覆盖首末页、页容量、跳页、总数、过滤后页码处理和数据变化；复杂表格还需验证现有排序、筛选、选择、展开与操作。原生 HTML / CSS 负责展示，不能替代这些数据和状态逻辑。

`components/visualization/VideoScatter/Toolbar.vue` 是项目组件，不能仅凭名称将其列入 PrimeVue 移除清单。

### 6. 暂缓范围与局部收尾

以下范围保持暂缓：

- 首页比赛卡片 `views/HomeView/NormalTournamentQueue.vue`：当前唯一 ElCard，带 header；按既定范围保留。
- 账号关联页面：将来重做时整体处理旧卡片与 Toolbar。当前残留的 ElButton / ElLink 主要在该目录，ElLink 另在首页比赛卡片中使用。
- PrimeVue 全量退出：按上一节独立推进，不阻塞本轮其他样式工作。

当前参与 lint 的页面限制新增 ElText、Element Plus 布局组件、ElCard 和 ElDivider；ElButton / ElLink 限制在 `src/**/*.vue` 中有以下 8 个文件例外：

- `views/HomeView/NormalTournamentQueue.vue`。
- `components/accountlinks/` 下的 `CardAdd.vue`、`CardAddMineracer.vue`、`CardBilibili.vue`、`CardSaolei.vue`、`CardWoM.vue`、`CarouselControl.vue`、`VideoImportQueue.vue`。

这些是按文件保留的兼容范围，不扩展为目录豁免；首页比赛卡片另有既存 ElCard 的局部 disable。迁移某个暂留文件后，同批清理其已不需要的规则例外。

每批完成后，删除对应失效导入、重复覆盖及无使用方的兼容样式，并更新剩余清单。复杂组件按功能保留，不以 Element Plus 导入归零作为本轮完成条件。

## 样式组织与冲突控制

- CSS / Less 的选型、styles 下的文件命名及目录组织由实施代理自行决定。每个项目样式目录文件不超过 100 个非空行，注释计入，不通过压缩声明规避限制。
- `src/styles/parameters/` 是 Git 忽略的本地参考存档，应用、测试、其他样式及构建脚本不得依赖它；需要参数时提取到正式样式文件。新检出项目应不需要该目录也能构建。
- 项目参数流向原生组件与库适配。库需要的 `--el-*` / `--p-*` 声明集中在 vendors，由项目变量赋值，不反向读取库变量。
- 优先使用公开 CSS 变量、组件样式接口，再使用局部内部选择器；覆盖集中在适配文件，避免业务页面散落大量覆盖或 `!important`。
- 保持现有文件路径、props、事件、slots 和调用方依赖的 attrs 稳定。按钮保留原生语义、键盘操作、disabled、loading、防重复点击及已有事件透传。
- 每个 PR 限定一个结果和一小组相关文件。共享样式与业务模块迁移可拆开；不同时做本地化调整、搬目录、整文件格式重排或无关逻辑抽离。
- 每批从最新集成分支开始，及时合入；正在频繁修改的业务区域可后移，允许新旧样式共存。
- 修改前核对工作区与最新内容，保留无关改动；两次修改之间发生的不同意的变化按约定添加 TODO，不直接覆盖。`lintfix` 后再次检查 diff。

具体样式入口和变量说明见[`src/styles/README.md`](src/styles/README.md)。

## 后续批次的验证与验收

按实际改动选择检查范围；已提交或明确验收的批次不重新追加验收待办。

| 范围 | 验收重点 |
| --- | --- |
| 视觉 | 深浅主题、直角、紧凑间距、文字语义、数字对齐、中英文长文本；有色单元格引用主题文字色 |
| 组件宽度 | 固定视口下改变容器宽度，检查伸缩、换行、内部滚动，以及少数布局切换组件的状态保持 |
| 操作 | 键盘焦点、hover、disabled、loading、错误状态、防重复提交 |
| 表格 | 空数据、加载、分页、排序、筛选、选择/展开、列宽与独立单元格操作，按实际使用能力检查 |
| 浮层 | 关闭、焦点、滚动、层级，以及传送到 body 的内部下拉框 |
| 业务 | 请求参数、提交次数、状态持久化、权限与删除确认行为保持一致 |

代码或样式修改按影响范围在 `front_end` 执行：

```powershell
npm.cmd run lintfix
npm.cmd run typecheck
npm.cmd run build:frontend
```

纯逻辑修改再运行对应 Vitest；例如颜色逻辑使用 `npx.cmd vitest run src/utils/colors.test.ts`。仅整理 Markdown 时检查内容、链接与 diff，不要求重跑前端构建。

Cypress 由用户运行，代理不启动 Cypress、预览或开发服务器。每批提供具体受影响的 spec 命令，优先复用现有覆盖；静态检查通过不代表浏览器行为已验证。迁移组件时才调整依赖 `.el-*` / `.p-*` 的测试定位，不提前全量改写。

复用项目现有表格提取、通知关闭和 `cy.shouldBeAbsentOrHidden()` 断言命令；不为低影响样式调整编写重复实现的测试，也不靠修改预期值掩盖实际行为变化。

提交或明确验收后按约定移除对应实施与验收待办；下一批建议始终以本计划的剩余范围及当时实际代码为准。
