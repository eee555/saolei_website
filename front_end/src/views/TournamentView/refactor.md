已实现：`front_end\src\views\TournamentView\common\PublicTournament.vue`，由 GSC 和周赛页面复用。以下记录布局与行为约定。

- 比赛标题：使用调用方提供的`tournament` prop
- 比赛描述：调用方通过`description` slot 自行渲染
- 参赛引导：调用方通过`participationGuide` slot 自行渲染及处理交互
- 自动上传：通过`autoUploaderFilter` slot 渲染筛选控件，通过`auto-uploader-enabled` prop 控制是否启用自动上传，通过`auto-uploader-filter` prop 提供筛选函数。
  - 开始自动上传后，尽量不卸载handler，而是通过暂停/继续轮询控制自动上传状态。
  - 保留监听器直到组件卸载；失去上传权限、参赛时间结束或参赛记录失效时暂停。处理文件时通过可选的 Badging API 设置无数字标记，空闲和卸载时清除，不支持时不影响上传。
- 比赛数据：用Tab渲染参赛者列表及单个参赛者的数据。前者依赖调用方提供的`participants` prop，后者依赖调用方提供的`index` prop。当`index`为非法索引（`participants[index] === undefined`）时，说明未参赛。
  - 比赛处于`Awarded`状态时，使用`front_end\src\views\TournamentView\common\AllParticipants.vue`的动态tab，其可以自定义`personalSummary`和`allSummary`两个slot
  - 比赛处于`Ongoing`、`Finished`状态时，有两个固定tab：第一个是参赛者列表，第二个是本参赛者数据。复用`allSummary`和`personalSummary`两个slot，由调用方进行条件渲染。两个tab的label都需要刷新按钮，刷新相应的数据。其中参赛者列表的刷新和比赛类型相关，需要调用方提供函数；本参赛者数据刷新实际上就是加载参赛者录像数据，和比赛类型无关，由组件内部负责。未参赛时不显示第二个tab
  - 当自动上传正在工作时（轮询中，或者用户已结束轮询但是还有正在处理的任务），禁用本参赛者数据刷新按钮。反过来，个人录像加载期间禁止开始和恢复上传。
  - 全部比赛录像数据导出由组件内部负责，控件放在“比赛数据”标题旁，仅在状态为`Awarded`时显示。
  - 暂时屏蔽下载某参赛者录像的功能


其他顺手修改的地方
- 移除 `displayState` getter，统一调用已有的 `getDisplayState(globalNow)`。按派生状态变化加载名单，不随每秒时钟重复请求；`Finished` 仍加载名单。GSC 从 `Preparing` 进入 `Ongoing` 时重新获取已公开的 token。
- 移除 AllParticipants 内原有的导出控件
- 自动上传相关：
  - `PollingDirectoryNewFileEmitter.start(emitExisting, pollIntervalMs)` 可覆盖构造参数。暂停保留 `knownFiles`，恢复时补扫新增文件。监听器等待文件处理完成再分发下一个文件，取消后不会重新启动定时器。
  - 初次启动时，弹窗告知用户当前文件夹中的文件数量，由用户选择是否直接补扫整个文件夹。如果用户选择扫描整个文件夹，在弹窗中显示进度条，并允许用户中断此次全量扫描（会直接退出轮询，用户需要重新选择文件夹）。
- 主办方/管理员删除participant后，需要同步处理`participants`和`index`。删除的操作在`allSummary` slot中，所以相应的交互由调用方负责。
- 刷新参赛者列表时，按participant ID保留本参赛者的数据。

实现分工：
- `common/useParticipants.ts` 管理名单加载、当前用户索引和对象保留；类型专属页面提供构造器和最终成绩 API。
- 各类型的 `AutoUploaderFilter.vue` 提供筛选控件和 `matchesFilter`，页面将函数和 slot 交给 `PublicTournament`。
- `common/PersonalView.vue` 管理个人录像请求；请求结果写入发起请求时的 participant，不会串到后来切换的参赛者。
- 全量扫描按已处理文件数显示进度，跳过和失败均计入。取消停止后续处理，已经发出的上传允许完成并归入原 participant。

验证：Vitest 覆盖目录监听器；Cypress 组件测试覆盖公共页面和上传器的交互，e2e 保留真实后端请求。Cypress 需手动运行。
