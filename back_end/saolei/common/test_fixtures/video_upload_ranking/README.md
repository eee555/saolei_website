# video_upload 排行联动测试录像

这个目录用于保存 `common.tests.VideoUploadRankingIntegrationTest` 需要的真实录像文件。
测试会通过 `common.views.video_upload` 上传这些文件，验证上传链路和 `tournament`、`msuser`、`customranking` 信号的联动。

当前需要的文件如下：

1. `standard_gsc.evf`
   - 普通三等级录像，建议使用高级标准录像。
   - 录像需要可以通过审核。
   - 录像内需要包含一个非空 GSC token，例如 `G12345`。
   - 测试会创建同 token 的进行中 GSC 比赛，并断言上传后录像进入比赛、`ongoing_tournament=True`，且不会刷新经典个人纪录。

2. `beginner_personal.evf`
   - 普通三等级初级录像，不应包含比赛 token。
   - 录像需要可以通过审核。
   - 测试会断言上传后经典个人纪录由 `msuser` 信号刷新。

3. `expert_personal.evf`
   - 普通三等级高级标准录像，不应包含比赛 token。
   - 录像需要可以通过审核。
   - 成绩应低于 `100000ms`，用于验证绑定标识后录像从 `IDENTIFIER` 变为 `OFFICIAL` 时会刷新 `video_num_limit`。

4. `custom_pluck.evf`
   - Density 排行支持的自定义级别录像，目前可用配置为：
     - `8x8/40`
     - `16x16/100`
     - `16x30/150`
     - `24x30/200`
   - 模式必须是 `STD`、`NF` 或 `RKC` 之一。
   - 录像需要可以通过审核。
   - 测试会先通过上传接口创建录像，再模拟后台任务写入 `pluck`，并断言 `CustomPluckRecord` 被信号刷新。

注意：
- 文件名可以保持如上固定名称，测试按这些文件名读取。
- 测试会自动解析录像标识，并为测试用户创建安全标识绑定。
- 缺少文件时，对应测试会被 `skip`，不会阻塞当前测试套件。
