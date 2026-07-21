# Minesweeper Tournaments

The website currently mainly supports the [Golden Sheep Cup](./gsc.md). If you want to host a tournament, you can contact the developers to add a new tournament mode.

## Tournament Identifiers

Only Minesweeper replays created during a tournament can participate in that tournament. For offline Minesweeper software, a tournament identifier is needed to prove that the replay is valid.

When the tournament starts, the server generates a random tournament identifier. You need to set this identifier in your Minesweeper software. Replays created afterward will contain the identifier. When you upload those replays, the server recognizes the tournament identifier and automatically marks them as tournament replays. When the tournament ends, the server stops accepting new tournament replays, ensuring that all tournament replays were created during the tournament.

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

## FAQ
