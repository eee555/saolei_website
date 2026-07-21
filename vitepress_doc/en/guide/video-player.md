# Video Player

Open Minesweeper provides three replay players: the native website player, [flop-player](https://github.com/hgraceb/flop-player), and [MSRA by StrangeDust](https://strange-dust.github.io/minesweeper-replay-analyzer/).

## Native Player

The native player is built into the website. It uses [`@putianyi888/vue3-minesweeper-board`](https://www.npmjs.com/package/@putianyi888/vue3-minesweeper-board) on the frontend and [`ms-toollib`](https://www.npmjs.com/package/ms-toollib) on the backend. In addition to basic replay playback, the native player supports custom counters. Custom counters use [`expr-eval`](https://www.npmjs.com/package/expr-eval) syntax. Assignment and function definitions are not supported. The supported fields are:

| Field | Description |
| --- | --- |
| `rtime`, `rtime_ms` | Total time |
| `etime` | estime |
| `bbbv`, `bbbv_s`, `bbbv_solved` | BV-related values |
| `ce`, `cl`, `ce_s`, `cl_s` | Click statistics |
| `rqp`, `stnb` | Other speed parameters |
| `cell0-8` | Number of each digit |
| `row`, `column`, `mine_num` | Custom board settings: rows, columns, mines |
| `level` | [Level](https://docs.rs/ms_toollib/latest/ms_toollib/videos/base_video/struct.BaseVideo.html#structfield.level) |
| `mode` | [Mode](https://docs.rs/ms_toollib/latest/ms_toollib/videos/base_video/struct.BaseVideo.html#structfield.mode) |
| `corr`, `thrp`, `ioe` | Efficiency parameters |
| `lce`, `rce`, `dce` | Effective clicks by button |
| `left`, `right`, `double` | Clicks by button |
| `left_s`, `right_s`, `double_s` | Clicks per second by button |
| `flag`, `flag_s` | Flagging parameters |
| `hzini`, `zini` | ZiNi |
| `op`, `isl` | Openings and islands |
| `video_end_time`, `video_start_time` | Timestamps |
| `game_board_state` | [Game state](https://docs.rs/ms_toollib/latest/ms_toollib/videos/minesweeper_board/enum.GameBoardState.html) |
| `mouse_state` | [Mouse state](https://docs.rs/ms_toollib/latest/ms_toollib/videos/minesweeper_board/enum.MouseState.html) |
| `path` | [Mouse path length](https://docs.rs/ms_toollib/latest/ms_toollib/videos/types/struct.GameDynamicParams.html#structfield.path) |
| `pix_size` | Cell size |
| `pluck` | |
| `current_event_id` | Current event index |
