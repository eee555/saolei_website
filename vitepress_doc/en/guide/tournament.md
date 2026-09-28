---
title: Tournaments - Open Minesweeper
description: Tournament features on Open Minesweeper, including scoring system, ranking points, tournament tokens and participation guide.
---

# Minesweeper Tournaments

The website currently mainly supports two tournament formats: the Golden Sheep Cup and the Weekly Tournament. If you want to host a tournament, you can contact the developers to add a new tournament mode.

Please check each tournament page for its rules, schedule, registration method, and other details.

## Tournament Points

After each tournament ends, tournament points are awarded to each participating user. Tournament points consist of two parts: ranking points and prize points. Points decay automatically over time, halving every 2 years.

The system records each user's historical best result in the Golden Sheep Cup and the Weekly Tournament separately. Historical best results are updated only from tournaments that have already been awarded.

### Ranking Points

Ranking points are calculated automatically based on a user's rank in the tournament. The formula is `1/rank`. For example, if a user finishes 5th, their ranking points are `1/5=0.2`. Each tournament has a ranking point coefficient, and this coefficient is multiplied into the ranking points. For example, if a points tournament has a ranking point coefficient of 50, the user receives `0.2*50=10` ranking points.

| Tournament | Coefficient |
| --- | --- |
| Golden Sheep Cup | 1000 |
| Weekly Tournament | 50 |

### Prize Points

If the organizer awards prize money to players, points are calculated from the prize amount. This is not supported yet.

### Point Decay

Point decay is calculated after each tournament ends and before new points are awarded. Each user's existing points are multiplied by a decay coefficient. The formula is `1/2^((current time - last update time)/2 years)`.

## Tournament Identifiers

Only Minesweeper replays created during a tournament can participate in that tournament. For offline Minesweeper software, a tournament identifier is needed to prove that the replay is valid.

The server generates a random tournament identifier, but a participant's identifier is only revealed at their participation start time (`start_time`). Registering early does not reveal it early. You need to set this identifier in your Minesweeper software. Replays created afterward will contain the identifier. When you upload those replays, the server recognizes the tournament identifier and automatically marks them as tournament replays. When the participant's time window ends, the server stops accepting their new tournament replays.

A replay can contain multiple tournament identifiers, separated by commas.

## Setting a Tournament Identifier

<details>
    <summary>MetaSweeper</summary>
    <span>Open Settings - Game Settings from the menu bar, or press S to open the settings window.</span>
    <img src="/tournament/metasweeper-token-zh.png" />
</details>
<details>
    <summary>Minesweeper Arbiter</summary>
    <span>Minesweeper Arbiter itself does not support tournament identifiers. Please follow the identifier rules set by the tournament organizer.</span>
</details>

## Tournament Replays

After a replay is recognized as belonging to an ongoing tournament, it is hidden and only the replay owner can see it. This means all leaderboards on the website ignore tournament replays. After the tournament ends, the system makes replays that no longer belong to an ongoing tournament publicly visible again and refreshes the leaderboards.

## Automatically Uploading Tournament Replays

If your browser supports [`showDirectoryPicker`](https://developer.mozilla.org/docs/Web/API/Window/showDirectoryPicker), you can use automatic uploading in Golden Sheep Cups and Weekly Tournaments. After registering, select a replay folder and polling interval during your participation window to scan, filter, and upload new files. Each filter level also applies all preceding conditions.

### Weekly Tournaments

1. All tournament videos: the tournament identifiers include your participation token. AVF is not supported.
2. Supported tournament videos: classic tournaments accept Intermediate and Expert replays in Standard or NF mode. This is the default filter.
3. Score-improving videos: the replay improves your total time for the best 5 Intermediate or 2 Expert games.

### Golden Sheep Cup

1. All tournament videos: AVF replays must have a nonempty player identifier that exactly matches your registered Arbiter identifier. For other software, the tournament identifiers must include this tournament's token.
2. Supported levels and modes: Beginner, Intermediate, or Expert in Standard or NF mode. This is the default filter.
3. 3BV minimum met: at least 10 for Beginner, 30 for Intermediate, and 100 for Expert.

Personal replays cannot be refreshed while monitoring or processing files. Automatic uploading cannot start while personal replays are loading.
