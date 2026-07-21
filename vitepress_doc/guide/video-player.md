# 录像播放器

开源扫雷网有三种录像播放器供选择：网站原生、[flop-player](https://github.com/hgraceb/flop-player)和[MSRA by StrangeDust](https://strange-dust.github.io/minesweeper-replay-analyzer/)。

## 原生播放器
原生播放器是网站自带的录像播放器，使用[`@putianyi888/vue3-minesweeper-board`](https://www.npmjs.com/package/@putianyi888/vue3-minesweeper-board)前端和[`ms-toollib`](https://www.npmjs.com/package/ms-toollib)后端。除了基本的录像播放功能以外，原生播放器还支持自定义计数器，自定义计数器使用[`expr-eval`](https://www.npmjs.com/package/expr-eval)的语法，不支持赋值与函数定义，支持的字段如下

|字段名|描述|
|---|---|
|`rtime`, `rtime_ms`|总用时|
|`etime`|estime|
|`bbbv`, `bbbv_s`, `bbbv_solved`|Bv相关|
|`ce`, `cl`, `ce_s`, `cl_s`|点击参数|
|`rqp`, `stnb`|其他速度参数|
|`cell0-8`|各数字的数量|
|`row`, `column`, `mine_num`|自定义配置：行数、列数、总雷数|
|`level`|[级别](https://docs.rs/ms_toollib/latest/ms_toollib/videos/base_video/struct.BaseVideo.html#structfield.level)|
|`mode`|[模式](https://docs.rs/ms_toollib/latest/ms_toollib/videos/base_video/struct.BaseVideo.html#structfield.mode)|
|`corr`, `thrp`, `ioe`|效率参数|
|`lce`, `rce`, `dce`|分键ce|
|`left`, `right`, `double`|分键cl|
|`left_s`, `right_s`, `double_s`|分键cls|
|`flag`, `flag_s`|标雷参数|
|`hzini`, `zini`|ZiNi|
|`op`, `isl`|空岛|
|`video_end_time`, `video_start_time`|时间戳|
|`game_board_state`|[游戏状态](https://docs.rs/ms_toollib/latest/ms_toollib/videos/minesweeper_board/enum.GameBoardState.html)|
|`mouse_state`|[鼠标状态](https://docs.rs/ms_toollib/latest/ms_toollib/videos/minesweeper_board/enum.MouseState.html)|
|`path`|[鼠标轨迹长度](https://docs.rs/ms_toollib/latest/ms_toollib/videos/types/struct.GameDynamicParams.html#structfield.path)|
|`pix_size`|格子大小|
|`pluck`||
|`current_event_id`|当前的时间索引|

