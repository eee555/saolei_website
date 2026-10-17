# ms-toollib 特征分析与逐事件 pluck 调研

核查日期：2026-10-12。重点是 `analyse_for_features(['pluck'])` 生成的逐事件数值。本次记录调查结论，尚未给 Analyzer 开启特征分析或新增表达式变量。

当前决定（2026-10-12）：用户已提交 pluck 相关 feature request，Analyzer 暂不支持 pluck。暂不采用修改 `current_event_id` 后读取 getter 的提取方案，不增加 pluck 计数器变量、自定义事件变量或 plot 数据；待上游接口更新后重新核查并评估接入。以下调用示例和验证结果保留为调研记录，不作为当前实施任务。

## 核查依据

- 当前项目实际安装 `ms-toollib@1.5.19`，检查了 `ms_toollib.d.ts`、生成的 JavaScript 和真实 WASM；AVF、EVF、MVF、RMV 均有 `analyse_for_features(f: string[]): void` 和 `video.pluck`。
- 算法说明来自本地上游源码快照 `994bd2305235dbe08bca4d34dbcc0187bd720ef0`，不将该快照视为 npm 1.5.19 的精确发布源码或当前 main。关键调用与读取行为另用已安装的 1.5.19 验证。
- 上游来源：[特征分派](https://github.com/eee555/ms-toollib/blob/994bd2305235dbe08bca4d34dbcc0187bd720ef0/base/src/videos/base_video.rs#L514)、[pluck 算法](https://github.com/eee555/ms-toollib/blob/994bd2305235dbe08bca4d34dbcc0187bd720ef0/base/src/videos/analyse_methods.rs#L283)、[播放阶段 pluck getter](https://github.com/eee555/ms-toollib/blob/994bd2305235dbe08bca4d34dbcc0187bd720ef0/base/src/videos/base_video.rs#L760)、[WASM 绑定](https://github.com/eee555/ms-toollib/blob/994bd2305235dbe08bca4d34dbcc0187bd720ef0/wasm/src/board.rs#L577)。部分上游旧注释与实现不一致，以下采用实际分派和算法。

## pluck 何时生成、如何读取

调用顺序是 `parse()` → `analyse()` → `analyse_for_features(['pluck'])`。普通 `analyse()` 不填充逐事件 pluck；七个样本在播放阶段调用该特征前读取 `video.pluck` 均为 `NaN`，之后得到随事件累积的数值。该方法返回 `undefined`，结果写回录像内部。

Rust 的 `KeyDynamicParams` 已有 `pluck` 字段，初始值为 `NaN`。特征分析将计算值写入事件快照，并写入录像的分析汇总字段。但 **npm 1.5.19 的 JavaScript `KeyDynamicParams` 没有 pluck getter**，类型声明和运行时原型均未暴露；调用后也不会新增一个 JavaScript 属性。因此直接读取 `event.key_dynamic_params.pluck` 不可用。

播放阶段可以用两种方式读取同一份已计算的事件值：

```ts
video.analyse_for_features(['pluck']);

// 页面 currentMs 是毫秒；ms-toollib current_time 使用秒。
video.current_time = currentMs / 1000;
const atTime = video.pluck;

// 按原始事件索引读取，能够区分同时间戳的不同事件。
const savedIndex = video.current_event_id;
try {
    video.current_event_id = eventIndex;
    const atEvent = video.pluck;
    // 使用 atEvent。
} finally {
    video.current_event_id = savedIndex;
}
```

`currentMs` 是 Analyzer 的状态，库没有同名接口。`current_time` 根据时间选择事件，`video.pluck` 在 Display 状态下直接返回 `current_event_id` 对应的缓存值，并不在每次 getter 时重新计算概率。WASM 录像类的索引 setter 直接赋值，不同步播放时间；不能将设置索引视为完整的页面定位操作。**只提取 pluck 时不需要改时间**，但要恢复索引，避免后续棋盘、光标等读取停留在另一个事件。

调研确认当前依赖技术上能通过索引遍历获得完整 pluck 序列，但用户决定暂不采用此方案。若上游以后补充 `KeyDynamicParams.pluck` getter，可重新验证直接读取事件快照的方案；不要在每毫秒采样或每次表达式求值时反复定位页面录像。

## 数值口径

- pluck 累积安全操作的 `-log10(安全概率)`；第一笔 `useful_level == 2` 的有效左键作为开始，值为 0，不计入首次开局风险。
- 后续有效左键使用操作前局面的安全概率；有效双键使用邻域待打开格子**共同安全的联合概率**，不能用独立概率相乘代替。
- 已核查源码在鼠标事件上保存累计值；不能据此假定任意扩展非鼠标事件也已填值。本次七个样本的整个序列均为有限数字，未覆盖人为新增的非鼠标事件。
- 踩雷或零安全概率时，特征分析写入 `f64::MAX`，JavaScript 为 `Number.MAX_VALUE`（`1.7976931348623157e+308`），本次失败 EVF 已复现。它不是 `Infinity`，不能擅自替换为无穷或 0。
- Rust 的 Win/Loss 状态 getter 还存在另一条计算分支；这里研究的是解析录像后的 Display 播放路径，不将实时游戏 getter 的规则混同为录像序列规则。

## 真实 WASM 验证

在 Node 24.18.0 中直接加载当前包的 WASM。每个样本新建解析对象，只调用 `['pluck']`，避免其他特征提前计算概率缓存。以下为一次运行，包含 WASM 热身及概率计算差异，不是浏览器性能保证。

| 录像 | 事件数 | 特征分析耗时 ms | 最后事件的 pluck |
| --- | ---: | ---: | ---: |
| `52200.evf` | 2473 | 168.67 | 0.08109874939134086 |
| `c_10_129.073_24_0.186_Pu Tian Yi(Hu Bei).evf` | 9169 | 6.63 | 6.539216403539405 |
| `c_10_39.832_24_0.477_Pu Tian Yi(Hu Bei)_fail.evf` | 4493 | 2.88 | Number.MAX_VALUE |
| `standard_gsc.evf` | 7845 | 95.93 | 0 |
| `Exp_FL_35.09_3BV=132_3BVs=3.76_Pu Tian Yi(Hu Bei).avf` | 6075 | 50.01 | 0.07989378842551652 |
| `Lin_Jin_Fan_Exp_60.623bv207.mvf` | 2060 | 65.30 | 0.713473263642931 |
| `3819-Time-1616-NF-9469-32-20151031.rmv` | 731 | 5.96 | 0.21741280087982903 |

同一次运行，遍历索引、生成数字数组并比对已提取序列用时约 0.24–2.26 ms，未包含事件包装对象复制与后续表达式采样成本。验证还确认：

- 调用特征前后，当前事件索引、当前局面及事件数量不变；pluck 分析不生成事件注释。
- 重复执行 `['pluck']` 后，逐事件数值与第一次完全一致。
- `52200.evf` 从原始事件索引 66 开始，pluck 从 0 变为 0.08109874939134086，后续保持该累计值。
- 129 秒 EVF 的 2 秒位置为 0，而最后事件为 6.539216403539405，证实 getter 返回当前位置的值，而非固定最终汇总。
- 四种录像类的事件参数运行时原型都没有 pluck getter。

复现脚本：[research-ms-toollib-pluck.mjs](../../../scripts/research-ms-toollib-pluck.mjs)。在 `front_end` 执行：

```powershell
node --experimental-wasm-modules scripts/research-ms-toollib-pluck.mjs
```

脚本使用 Node 的实验性 WASM 模块加载，运行时会输出相应提示；不需要开启开发服务器或 Cypress。每个样本都会释放事件、参数包装对象和录像对象。本次未做浏览器交互或大型录像性能验收。

## 其他特征的输出

已安装版本的四种录像类均可执行下列七个 key。除 pluck 外，主要输出是事件已有 `comments` 字符串中的分号分隔注释，并不增加 `KeyDynamicParams` 的数值 getter。

| 调用 key | 注释或结果 | 实际含义 |
| --- | --- | --- |
| `pluck` | 内部逐事件 pluck，可经 `video.pluck` 读取 | 累积操作风险，无 comments 注释。 |
| `high_risk_guess` | `error:high_risk_guess:<安全概率>;` | 检查到雷概率 ≥ 0.51 的有效操作；载荷是安全概率。 |
| `jump_judge` | `feature:hard_judgment:left;` / `feature:hard_judgment:flag;` | 枚举可判、基础方法不能判的左键或标雷。 |
| `needless_guess` | `warning:needless_guess;` | 猜雷时邻近 5×5 范围存在可判安全格。 |
| `mouse_trace` | `error:mouse_trace_too_curved:<百分比>;` / `warning:mouse_trace_curved:<百分比>;` / `suspect:mouse_trace_straight;` | 路径/直线距离 >20、>10 或 <1.01；注释附到此前的点击事件。 |
| `vision_transfer` | `warning:vision_transfer;` | 远距离转移时，原位置附近仍有可判安全格；注释附到此前点击。源码有 `// bug` 标记，宜保留实验性质。 |
| `super_fl_local` | `feature:fl_local:<操作计数>;` | 局部 FL 状态机识别到序列后，注释附到起始锚点；调用 key 与输出名称不同。 |

先前对六个样本逐项调用了全部七种特征，均正常返回。重复 `mouse_trace` 会追加重复注释，不能把注释分析当作幂等调用；调用前取得的事件包装对象是快照，也不会自动得到后来追加的注释。读取注释应在分析后重新获取事件，并释放包装对象。上述源码分派遇到不支持的 key 会 panic；旧注释提到的 `survive_poss` 不在实际支持列表。

`useful_level` 已由普通 `analyse()` 生成并暴露，属于另一项可扩充的数值事件字段，无需调用特征分析。注释字符串则不能直接当作目前要求数字结果的计数器值；后续若需要内置特征事件，应明确解析和事件归属规则，保留原始事件索引，避免毫秒去重吞掉标注。

## Analyzer 当前决定与后续核查

目前 `components/VideoAnalyzer/replayParser.ts` 只调用 `parse()` 和 `analyse()`，`counter.ts` 的 34 个变量尚无 pluck。用户已提交相关 feature request，当前暂不调用 `['pluck']`，不扩充表达式变量。待上游接口更新后，核查 JavaScript 类型声明与运行时 getter、分析调用顺序、逐事件值、失败值和非鼠标事件，再评估接入现有计数器、自定义事件与 plot；若接入，沿用现有三种采样、毫秒去重及插值。

特征分析有概率计算成本，宜按使用需求执行并按源缓存；用于视频绘制的独立导出解析对象无需计算未参与画面的指标。未分析时的 `NaN` 应与真实 0 区分。事件原始数组、时间及数量保持不变，初始化提取必须恢复索引，不能让分析影响播放状态。

已提交的 pluck feature request 与已停止的完整数值快照请求分别记录，不恢复完整快照请求；后者的过时文档已删除。研究脚本保留用于后续复核，不是 Analyzer 的功能入口。
