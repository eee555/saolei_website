---
title: 录像播放器 - 开源扫雷网
description: 开源扫雷网的三种录像播放器：网站原生播放器、flop-player和MSRA，支持自定义计数器和丰富的扫雷数据字段。
---

# 录像播放器

开源扫雷网有三种录像播放器供选择：网站原生、[flop-player](https://github.com/hgraceb/flop-player)和[MSRA by StrangeDust](https://strange-dust.github.io/minesweeper-replay-analyzer/)。

## 原生播放器
原生播放器是网站自带的录像播放器，棋盘由 [`@putianyi888/vue3-minesweeper-board`](https://www.npmjs.com/package/@putianyi888/vue3-minesweeper-board) 渲染，录像由 [`ms-toollib`](https://www.npmjs.com/package/ms-toollib) 解析。除了基本的录像播放功能，还支持使用 `expr-eval` 语法的自定义计数器。

字段、运算符、条件与逻辑运算、内置函数，以及与录像分析页计数器和自定义事件的差异，详见[录像表达式参考](./replay-expressions)。

