# VideoAnalyzer

项目内可复用分析组件，入口为 `src/components/VideoAnalyzer/index.ts`。子组件、解析、采样、播放、主线程导出及对应测试都在本目录；站内页面包装和计划文档仍在 `src/views/VideoAnalyzerView/`。

```vue
<VideoAnalyzer v-model:config="config" v-model:probability-color-scheme="probabilityColorScheme" v-model:exporting="exporting" :source="source" title="录像分析">
    <template #info>调用方提供的信息</template>
</VideoAnalyzer>
```

```ts
import { ref, shallowRef } from 'vue';
import VideoAnalyzer, { defaultAnalyzerConfig } from '@/components/VideoAnalyzer';
import type { ReplaySource } from '@/components/VideoAnalyzer';

const source = shallowRef<ReplaySource | null>(null);
const config = ref(defaultAnalyzerConfig());
const probabilityColorScheme = ref({ colors: ['#15803d', '#dc2626'], thresholds: [50] });
const exporting = ref(false);
// 调用方获取字节后，替换 source.value：
// { data: ArrayBuffer, filename: string, software: 'a' | 'e' | 'm' | 'r' }
```

| 接口 | 约定 |
| --- | --- |
| `source` | 普通录像字节及格式；组件自己解析和释放 WASM 对象。更换文件时替换整个对象，不原地修改字节；传 null 清空。 |
| `loading` / `errorMessage` | 调用方的文件读取或站内请求状态；解析错误由组件显示。 |
| `title` / `filename` | 可选分析区域的可访问名称和导出文件名前缀；不显示顶部标题，区域名称默认采用本地化的“录像分析”，导出默认采用 source.filename。 |
| `v-model:config` | 配置由调用方保存；未提供时每个实例独立创建默认设置，不读 localStorage。 |
| `v-model:probabilityColorScheme` | 必须提供概率配色；站内包装页绑定原有共享配色，其他入口自行保存。 |
| `v-model:exporting` | 导出期间为 true，调用方据此禁止更换文件或离开路由。组件卸载时中止导出。 |
| `#info` | 宽容器与计数器共享面板，窄容器置顶；未传 slot 时不保留空区域。 |

每个实例持有独立解析对象、播放时钟、进度、区间、关键帧和采样数据。替换源重置录像状态；布局切换不重新解析。导出使用独立解析副本，不推进可见录像。

默认计数器为 `Bvs`、`Ces`、`Mov`，均连续采样、显示格式 `.3f`，用 `d(..., 1000)` 计算差分速率；`Mov` 再除以 16。Plot 1 包含 `Bvs` 和 `Ces`，Plot 2 包含 `Mov`。不再默认提供小写 `bvs`，已保存配置不覆盖。完整公式见[表达式参考](../../../../vitepress_doc/guide/replay-expressions.md#默认计数器)。

布局设置位于棋盘右下角、格子大小控件上方。单个布局按钮点击后打开交互式 tooltip，内含“自动”和四种预设的下拉框；选择后关闭，支持 Escape 关闭。加载或报错期间仍可切换布局，配置继续由 `v-model:config` 保存。

组件不直接请求站内 API、导入路由或持有持久化配置单例。它继续使用项目 CSS、Vue I18n、基础控件、帮助链接、通知及剪贴板 helper；后两者使用独立的 `store/local.ts` 设置模块。离线入口及资源内联已实现，首次本地包已生成，真实 file:// 验收及 CI 仍待完成，见 [离线构建说明](../../views/VideoAnalyzerView/OFFLINE_BUILD_README.md)。

离线入口将 `#info` 内容换成选择本地录像文件的控件，读取字节后更新 `source`；选择控件沿用 slot 的宽窄容器布局，并在 `exporting` 为 true 时禁用。分析器其余区域及功能直接复用。在 `front_end` 执行 `npm.cmd run build:offline`，生成 `OpenMinesweeperVideoAnalyzer-${version}.zip`，独立版本由 `local-analyzer/version.json` 提供。

站内包装页默认通过 info slot 提供四行网站信息：录像 ID/上传时间、PlayerName/可选比赛 ID、该录像的各榜名次、文件名；右侧独立按钮列提供 StrangeDust Analyzer 链接和离线包下载图标。网站信息请求、PlayerName、比赛、外部分析及下载链接均留在包装页目录，不进入公共组件；信息加载失败不阻塞文件解析与播放或离线包下载。

单元测试：`npx.cmd vitest run src/components/VideoAnalyzer src/views/VideoAnalyzerView`。Cypress 由用户运行：

```powershell
npx.cmd cypress run --component --browser chrome --headless --spec "src/components/VideoAnalyzer/AnalyzerLayoutControl.cy.ts,src/components/VideoAnalyzer/App.cy.ts,src/components/VideoAnalyzer/BoardPanel.cy.ts,src/components/VideoAnalyzer/VideoExport.cy.ts,src/views/VideoAnalyzerView/App.cy.ts,src/views/VideoAnalyzerView/WebsiteReplayInfo.cy.ts"
```
