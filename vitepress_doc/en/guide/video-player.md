---
title: Video Player - Open Minesweeper
description: "Three replay players available on Open Minesweeper: native player, flop-player and MSRA, with custom counter support."
---

# Video Player

Open Minesweeper provides three replay players: the native website player, [flop-player](https://github.com/hgraceb/flop-player), and [MSRA by StrangeDust](https://strange-dust.github.io/minesweeper-replay-analyzer/).

## Native Player

The native player is built into the website. Its board is rendered by [`@putianyi888/vue3-minesweeper-board`](https://www.npmjs.com/package/@putianyi888/vue3-minesweeper-board), and replays are parsed by [`ms-toollib`](https://www.npmjs.com/package/ms-toollib). Besides playback, it supports custom counters using `expr-eval` syntax.

See [Replay Expressions](./replay-expressions) for fields, operators, conditional and logical expressions, built-in functions, and differences from analyzer counters and custom events.
