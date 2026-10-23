# 勋章图片

勋章页面会在低带宽环境下同时展示多枚图片。后续新增系列、档位或一次性勋章时，必须使用统一生成脚本和资源预算，不能把模板原图直接放到页面。

## 文件与生成方式

源模板放在`front_end/src/assets/medal-templates/`，发布文件由`front_end/scripts/build_medal_art.py`生成到`front_end/public/assets/medals/`。

脚本先在320×320画布完成裁切、金属换色和档位数字，再缩小为72×72。发布格式固定为带透明通道的WebP，编码参数为`quality=60`、`alpha_quality=50`、`method=6`。所有输出必须经过脚本的`save_art()`，不要在其他脚本中使用另一套尺寸或质量参数。

路径约定：

- 分难度的阶梯勋章：`{系列目录}/{b|i|e}/{整数阶段}.webp`。
- 不分难度的勋章：`{系列目录}/{整数阶段}.webp`。
- 阶段文件名使用后端保存的整数刻度。

图片可以包含由脚本生成的档位数字，不烘焙系列名、难度名和说明文字。页面用本地化文本显示完整称号。

## 资源预算

生成后的资源必须满足：

| 检查项 | 上限 |
| --- | ---: |
| 单张图片 | 4KiB |
| 全部勋章图片 | 700KiB |
| 每个系列/难度目录取最大图片后的合计 | 90KiB |
| 左栏6枚的保守上限 | 20KiB |

生成脚本会在每张图片写入后立即检查4KiB上限，超出时指出具体文件并终止。新增图片数量可以超过当前基线，但不能绕过单图上限。若新增系列使组合或全库预算不足，应先优化图片或页面加载方式，并提供新的传输量测量，再调整预算。

## 前端引用

展示图片时写明`width`和`height`，使用`loading="lazy"`、`decoding="async"`，并复用`medalArtUrl()`生成的统一URL。同一路径的内容或编码参数变化后，提高该URL的资源版本参数，避免浏览器继续使用旧文件。

## 检查步骤

从仓库根目录执行：

```powershell
.\back_end\saolei\.venv\Scripts\python.exe front_end\scripts\build_medal_art.py
.\back_end\saolei\.venv\Scripts\python.exe -m unittest discover -s front_end\scripts -p test_medal_art.py
```

自动检查覆盖WebP格式、72×72尺寸、透明通道、文件可解码和各项体积预算。提交前还要在浅色和深色背景下，以48×48和72×72检查轮廓、档位数字及透明边缘。
