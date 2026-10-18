---
title: Minesweeper Data - Open Minesweeper
description: Detailed explanation of minesweeper data metrics, including 3BV, ZiNi, bvs, rqp, ioe and stnb single-game data, plus historical systems such as the LSF system.
---

# Minesweeper Data

Minesweeper data are the metrics used to evaluate board complexity and player performance. The existing metrics can be roughly divided into single-game data and historical data.

- **Single-game data** are the data of one game. Single-game data are further divided into basic data and derived data.
  - [Basic data](#basic-data) are data that do not depend on any other data. Basic data are further divided into board data and input data.
    - [Board data](#board-data) are determined by the placement of mines and include [bv, op, is](#bv-op-is), [zini](#zini) and [cellx](#cellx).
    - [Input data](#input-data) are determined by the mouse operations the player performs and include [time](#time), [path](#path-cpath-epath), [cl, ce](#cl-ce) and [bvdone, opdone](#bvdone-opdone).
  - [Derived data](#derived-data) are computed from several basic data in order to evaluate the quality of one game.
    - based on bv and time: [bvs, rqp, qg, ios, rv](#bvs-rqp-qg-ios-rv).
    - for evaluating click speed: [ces, cls](#ces-cls).
    - for evaluating operation efficiency: [corr, thrp, ioe](#corr-thrp-ioe).
    - for evaluating the efficiency of handling openings: [cpo, coo](#cpo-coo).
    - based on path: [mov, sao, iome](#mov-sao-iome).
    - based on zini: [zinis, znt, zne](#zinis-znt-zne).
    - based on completion: [completion, estime, stnb](#completion-estime-stnb).
    - based on cells: [numbers, obg](#numbers-obg).

  `time`, `bvs` and `stnb` are the three most widely accepted single-game metrics for evaluating racing strength, and are called the **three major parameters**.
- **Historical data** are distilled from all of a fixed player's single-game data over an entire minesweeper career. At present the most popular kinds of historical data are the LSF system, the pb system and the player line system.
  - The [LSF system](#the-lsf-system) is a standard that rates a player's level based on the data of the country's top players.
  - pb is a player's historical best result on a specific bv. Combat power, typical time, typical stnb, the medal system and the head-to-head mechanism can all be derived from pbs.
  - The player line is the set of a player's strongest replays that do not beat each other. Coarse tiers, fine tiers and the mutual-knock mechanism can be derived from player lines.

_______
# Basic Data
Basic data are data specific to each replay that do not depend on any other data. Subdivided further, basic data can again be split into properties of the board itself (board data) and the player's input data.

Properties of the board itself include [bv, op, is](#bv-op-is), [the various zini](#zini) and [cellx](#cellx). The player's input data include [the various cl and ce](#cl-ce), [path](#path-cpath-epath) and [time](#time). Strictly speaking, the placement of mines is the most basic property of the board itself, and each click and the mouse trajectory are the most basic player input data, but these are too tedious to summarize and are generally not discussed.

## Board Data

#### `bv`, `op`, `is`
`bv` is short for `3BV`, `3BV` is short for `BBBV`, and `BBBV` is short for `Bechtel's Board Benchmark Value`. `bv` is the most classic parameter for measuring the complexity of a board.

`op` is short for `Opening`; in Chinese it is `空`.

`is` is short for `Island`; in Chinese it is `岛`. To avoid confusion with the English word "is", it is sometimes written `isl`.

[Wudi's column](https://zhuanlan.zhihu.com/p/27185883) explains in detail what `bv`, `op` and `is` mean and what role they play in board difficulty, so it is not repeated here.

### `zini`
If `bv` measures the lower bound of the number of NF operations needed for a board, `zini` measures the lower bound of the number of FL operations. The concept and algorithms of `zini` were proposed in 2009 by [Elmar Zimmermann](https://minesweepergame.com/profile.php?pid=322) and [Christoph Nikolaus](https://minesweepergame.com/profile.php?pid=173) on the [international forum](https://minesweepergame.com/forum//viewtopic.php?f=15&t=70), and are named after their surnames. Because finding the optimal FL solution for a board is an NP problem, i.e. it cannot be computed at a small cost, they instead looked for fast approximation algorithms. They proposed three greedy algorithms.

The core greedy idea is to find the operation with the greatest gain at each step. Given that all mine positions are known, every cell in a given board state has exactly one operation that can produce gain:
- Flag around this cell and chord on it; the gain is `bv opened by the chord - number of flags - 1`. If the cell is not yet opened, then taking the operation needed to open the cell into account, the gain is further reduced by 1. bv already opened and flags already placed are not counted. Chording directly is equivalent to a flag count of 0.

Starting from the beginning of the game, compute the gain of every non-mine cell at every step. If any cell has non-negative gain, choose the cell with the greatest gain and perform the corresponding operation; if all cells have negative gain, finish the remaining `bv` with left clicks. The number of operations used to finish a game this way is its `zini`. The three `zini` algorithms differ only in details.

`gzini` is short for "Greedy ZiNi": when several cells share the same greatest gain, it always picks the topmost-then-leftmost one. `rzini` is short for "Random ZiNi": when several cells share the same greatest gain, it picks one at random. The random sweeping is repeated until n consecutive games fail to set a new record for the fewest operations. `hzini` is short for "Human ZiNi": it first opens all `op` with left clicks and then behaves like `gzini`.

Obviously `rzini` still contains luck and is unstable, so it is generally not used as a metric. `gzini` and `hzini` are not ordered, and neither is unbeatable. Players have already beaten both `gzini` and `hzini` on beginner and intermediate (i.e. finished with fewer operations), but nobody has achieved this on expert yet. Both Minesweeper Arbiter and Metasweeper report `gzini` and `hzini`.

In recent years other variants of zini algorithms have appeared, the most notable being [Pttazini (PTTACGfans's ZiNi)](https://github.com/PTTACGfans/Minesweeper-ZiNi-Calculator).

### cellx
cellx is the number of cells showing the digit x. x ranges from 0 to 8.

## Input Data

### `time`
`time` is the time used to finish a game and is the most important metric in minesweeper.

Historically there have been two kinds of `time`. One starts counting from 1 second and belongs to Minesweeper Clone. The other starts counting from 0 seconds and belongs to Minesweeper Arbiter. The mainstream timing today starts from 0 seconds, but because the earliest Winmine started from 1 second, some concepts still follow the 1-second convention.
- Saolei.wang displays data timed from 1 second.
- (Very important, a must-read for insiders and bizarre trivia for outsiders) Traditionally, the concepts of seconds and sub are defined on the premise that timing starts from 1 second. For example, an intermediate time of 10 seconds means that, with timing starting from 1 second, the integer part is 10, which corresponds to `rtime` from 9.00 to 9.99. Expert sub40 means expert seconds sub40, i.e. expert seconds <= 39, i.e. `rtime<=38.99`.

Whichever timing convention is used, `rtime` (Real Time) is unambiguous and always means time counted from 0 seconds. The `time` mentioned on the rest of this page always means `rtime`.

### `path`, `cpath`, `epath`
`path` is the distance the cursor travels while finishing a game. The unit of `path` is pixels or cells, where 1 cell = 16 pixels.

`cpath`, short for Click Path, only considers the distance between the positions where click events happen and ignores the loss from curved mouse trajectories.

`epath`, short for Effective Path, only considers the distance between the centers of the cells of effective click events and ignores the difference in where inside a cell the mouse clicked.

### `cl`, `ce`
`cl` is short for "Clicks" and means the number of mouse clicks. `ce` is short for "Efficient Cl" and means the number of effective clicks. Broken down by click type there are also `lcl`, `rcl`, `dcl`, `lce`, `rce` and `dce`, where the prefix `l` is short for Left (left button), the prefix `r` is short for Right (right button) and the prefix `d` is short for Double (chord).

The difference between `cl` and `ce` is ineffective clicks. The reasons for ineffective clicks with the left, right and both buttons are:
- left click landing on a number or a flag; cancelling a left click; clicking a just-opened op during a continuous sequence because of slow reaction.
- right click landing on a number; misflagging; cancelling a misflag; wrongly cancelling a flag; re-flagging after wrongly cancelling a flag.
- chord landing wrong; cancelling a chord; a probing chord that fails.

The main disagreement between standards is about ineffective right clicks. Minesweeper Arbiter considers `ce` to be all operations that change the board, so misflags and cancelling flags both count as effective clicks. Open Minesweeper and Metasweeper are stricter and require an operation to be correct to count as `ce`.

### `bvdone`, `opdone`
bvdone means completed bv and opdone means completed op.

### `luck`, `pluck`
Both parameters are based on a probability engine. For every operation that opens a cell, the engine computes the safety probability (0-1) from the current board; multiplying the safety probabilities of all operations gives `luck`, which represents the theoretical win rate of a game. `pluck` is defined as `-log10(luck)`.

________________
# Derived Data

### `bvs`, `rqp`, `qg`, `ios`, `rv`
`bvs` is short for "bv/s"; the formula is `bvs=bv/time`, meaning the number of `bv` solved per second, and larger is better. `bvs` is the most classic speed metric, second only to `time` in importance. Generally a smaller `bv` gives a better `time`, while a larger `bv` gives a better `bvs`, so other parameters are needed to balance them.

`rqp` is short for "Rapport Qualité Prix"; the formula is `rqp=(time+1)/bvs`. The reason for adding 1 to the time is that the timing convention was still 1-based when this parameter was invented. If that 1 second is ignored when `time` is large, `rqp` is approximately `time^2/bv`. `rqp` values the role of `time` heavily, but it deviates when `time` is small, and the deviation is already serious when `time<60`.

`qg` is short for "Quality Grade", a strength parameter defined by [Guo Jinyang](https://openms.top/#/player/48) from a large amount of data; the formula is `qg=time^1.7/bv`. Compared with `rqp`, `qg` has the advantage of emphasising `bvs` more and removing the deviation at low times.

`ios` is short for "Index of Speed"; the formula is `ios=log(bv)/log(time)`.

`rv` is short for "Rirun Value"; the formula is `rv=sqrt(yybv*rqp+0.25)-0.5`. Here `yybv` is the `bv` used for wishful thinking, for example 100 for expert and 30 for intermediate.

### `ces`, `cls`
Similar to `bvs`, `ces=ce/time` and `cls=cl/time`. These two parameters represent the player's operation speed; `cls` focuses on the overall operation rate, while `ces` represents the conscious operation rate.

### `corr`, `thrp`, `ioe`
`corr` is short for "Correctness"; the formula is `corr=ce/cl`. Because ineffective clicks are in most cases not caused by misaiming (a player who misaims a lot can hardly finish a game), `corr` can actually reflect, to some extent, how much thought goes into the operations. Mindless chording sprees and combos that completely ignore potential `op` both lower `corr`.

`thrp` is short for "ThroughPut"; the formula is `thrp=bv/ce`. For FL, `thrp` reflects overall flag-and-chord efficiency. For NF, `thrp` reflects overall opening-breaking efficiency.

`ioe` is short for "Index of Efficiency"; the formula is `ioe=bv/cl`. `ioe` reflects overall operation efficiency.

Obviously we also have the following relations:
- `corr=ces/cls`
- `thrp=bvs/ces`
- `ioe=bvs/cls`
- `ioe=corr*thrp`

For NF, the only way to improve operation efficiency is to improve awareness of `op`; for NF the meanings of `ioe`, `thrp` and `corr` are much the same, and higher means stronger opening-breaking awareness. For FL, `corr` mainly reflects operation precision and the success rate of probing chords, while `thrp` reflects the efficiency of the optimization strategy. Because reasonable probing chords can produce gain, FL players should not over-pursue `corr`.

### `cpo`, `coo`
For NF, a low `thrp` in a single game may be caused not only by insufficient opening-breaking awareness but also by a bad board. In plain words, the more `op` a board has, the lower the `thrp`. To offset the influence of `op` fluctuations on `thrp`, two parameters were invented.

`cpo` is short for "avg Ce wasted Per Opening"; the formula is `cpo=(ce-bv)/op`. `coo` is short for "avg Ce cost On each Opening"; the formula is `coo=cpo+1`.

### `mov`, `sao`, `iome`
`mov` is short for "Movement"; the formula is `mov=path/time`, reflecting the overall mouse speed.

`iome` is short for "Index of Movement Efficiency"; the formula is `iome=bv/path`, reflecting the solving strategy. A low `iome` means a tendency to solve `bv` nearby, while a high `iome` means a tendency to look for optimal solutions over a wide area.

`sao` is short for "风骚度" (flair); the formula is `sao=mov*ces`, reflecting the overall intensity of operations.

### `zinis`, `znt`, `zne`
In the framework that uses `bv` as the measure of board complexity, `bvs` represents speed and `thrp` and `ioe` represent efficiency. `bvs`, `thrp` and `ioe` correspond to `zinis`, `znt` and `zne` in the framework that uses `zini` as the measure of board complexity:
- `zinis=zini/s`
- `znt=zini/ce`
- `zne=zini/cl`

For different `zini` algorithms, just change the corresponding `zini` prefix, for example `gzinis`, `rznt`, `hzne` and so on.

### `completion`, `estime`, `stnb`
`completion` means completeness; the formula is `completion=bvdone/bv`.

`estime` is short for "Estimated Time", meaning the projected time; the formula is `estime=time/completion`.

`stnb` is short for "尸体牛逼" (how awesome a corpse is) and measures how impressive a corpse is; the formula is `stnb=sqrt(completion)*constant/qg`. The constants for beginner, intermediate and expert are `36, 162, 435`; the purpose of the constant is to make `stnb` roughly equal across the three levels at the same skill level. It is precisely because of this constant that `stnb` is more popular than `qg` and is one of the most important "three major parameters".

> The constant can also be computed as `73.5*mode^2-94.5*mode+57`. This applies to custom counters that do not support branch logic.
> Before 2023-09-13 the constants were `47.299, 153.73, 435.001`, and the formula for computing the constant was `87.420*(mode^2)-155.829*mode+115.708`.

### `numbers`, `obg`
`numbers` is the sum of all numbers on a board; the formula is `numbers=0*cell0+1*cell1+2*cell2+3*cell3+4*cell4+5*cell5+6*cell6+7*cell7+8*cell8`.

`obg` measures the player's reaction speed to `bv`; the formula is `obg=10000*bvs/numbers`, where 10000 is purely to keep the value from being too small.

__________
# The LSF System

The top and LSF rankings use best-five results, anchors and relative strength to rate players. See [top and LSF Rankings](../top-lsf.md) for the current rules and tier system.

________
# References
1. [Guo Jinyang, "A Brief Discussion of Strength Parameters" (实力参数浅谈), Saolei.wang](http://www.saolei.wang/BBS/Title.asp?Id=9786)
2. [Lin Jinfan, "A Dictionary of Minesweeper Technical Metrics" (扫雷技术指标解析词典), Saolei.wang](http://www.saolei.wang/BBS/Title.asp?Id=12924)
3. [Guo Jinyang, "Advanced Minesweeper Technical Metrics" (进阶扫雷技术指标), Saolei.wang](http://www.saolei.wang/BBS/Title.asp?Id=12918)
4. [Zhou Ke, "A Brief Analysis of 3BV and ZiNi" (3BV与ZiNi浅析), Saolei.wang](http://saolei.wang/BBS/Title.asp?Id=6946)
5. [Zhao Shuang, "Minesweeper Terminology, 2nd Edition" (扫雷术语（第二版）), Saolei.wang](http://saolei.wang/BBS/Title.asp?Id=6919)
6. [Elmar Zimmermann, "new benchmark: 3bv for flaggers", Authoritative Minesweeper](https://minesweepergame.com/forum//viewtopic.php?f=15&t=70)
