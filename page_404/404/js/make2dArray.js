"use strict";
function make2dArray(rows, cols) {
    var arr = new Array(cols);
    for (var i = 0; i < cols; i++) {
        arr[i] = new Array(rows);
    }
    return arr;
}
var gameStatus;
(function (gameStatus) {
    gameStatus[gameStatus["NotReady"] = 0] = "NotReady";
    gameStatus[gameStatus["Playing"] = 1] = "Playing";
    gameStatus[gameStatus["Win"] = 2] = "Win";
    gameStatus[gameStatus["Fail"] = 3] = "Fail";
})(gameStatus || (gameStatus = {}));
