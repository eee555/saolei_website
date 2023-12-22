"use strict";
// const slider = <HTMLInputElement>document.querySelector('#mines');
// let numberOfMines = slider.value;
var canvas = document.querySelector('canvas');
var flaggedElement = document.getElementById('flagged');
var restartButton = document.querySelector('#replay');
var SIZE = 16; // 方格边长
var ROW = 32;
var COLUMN = 48;
var CANVAS_HEIGHT = SIZE * ROW;
var CANVAS_WIDTH = SIZE * COLUMN;
var MINENUM = 404;
canvas.height = CANVAS_HEIGHT;
canvas.width = CANVAS_WIDTH;
var game = new Game(canvas, ROW, COLUMN, MINENUM, SIZE);
restartButton.addEventListener('click', function () { game.reset(); game.gameStatus = gameStatus.NotReady; });
canvas.oncontextmenu = function () { return false; }; // 关闭右键菜单
canvas.addEventListener('mousedown', handleClickDown);
canvas.addEventListener('mouseup', handleClickUp);
canvas.addEventListener('mousemove', handleMouseMove);
canvas.addEventListener('mouseout', handleMouseOut);
var touchStart = 0;
var touchEnd = 0;
canvas.addEventListener('touchend', handleTouch);
canvas.addEventListener('touchstart', function (e) {
    e.preventDefault();
    touchStart = Date.now();
});
function handleClickDown(event) {
    event.preventDefault();
    if (game.gameStatus == gameStatus.Win || game.gameStatus == gameStatus.Fail)
        return;
    var rect = this.getBoundingClientRect();
    var y = Math.floor((event.clientX - rect.left) / game.cellWidth);
    var x = Math.floor((event.clientY - rect.top) / game.cellWidth);
    if (game.mouseRightHold || game.mouseLeftHold || game.mouseChordingHold_2) {
        game.mouseChordingHold = true;
        // console.log('把双击标志设为真')
        game.mouseRightHold = false;
        game.mouseLeftHold = false;
        game.mouseChordingHold_2 = false;
        for (var i = Math.max(x - 1, 0); i < Math.min(x + 2, game.rows); i++) {
            for (var j = Math.max(y - 1, 0); j < Math.min(y + 2, game.cols); j++) {
                if (!game.grid[i][j].flagged && !game.grid[i][j].revealed) {
                    game.grid[i][j].hold = true;
                    game.grid[i][j].show(this, gameStatus.Playing);
                }
            }
        }
        return;
    }
    if (event.button === 0) {
        game.mouseLeftHold = true;
        if (!game.grid[x][y].flagged && !game.grid[x][y].revealed) {
            game.grid[x][y].hold = true;
            game.grid[x][y].show(this, gameStatus.Playing);
        }
    }
    else if (event.button === 2) {
        game.mouseRightHold = true;
        if (!game.grid[x][y].revealed) {
            game.grid[x][y].flagged = !game.grid[x][y].flagged;
            game.grid[x][y].show(this, gameStatus.Playing);
        }
    }
}
;
function handleClickUp(event) {
    event.preventDefault();
    if (game.gameStatus == gameStatus.Win || game.gameStatus == gameStatus.Fail)
        return;
    var rect = this.getBoundingClientRect();
    var y = Math.floor((event.clientX - rect.left) / game.cellWidth);
    var x = Math.floor((event.clientY - rect.top) / game.cellWidth);
    if (game.mouseChordingHold) {
        game.mouseChordingHold = false;
        game.mouseChordingHold_2 = true;
        // console.log('双击回调')
        for (var i = Math.max(x - 1, 0); i < Math.min(x + 2, game.rows); i++) {
            for (var j = Math.max(y - 1, 0); j < Math.min(y + 2, game.cols); j++) {
                game.grid[i][j].hold = false;
                game.grid[i][j].show(this, gameStatus.Playing);
            }
        }
        // console.log('双击回调2')
        if (game.grid[x][y].revealed) {
            var flagNum = 0;
            for (var i = Math.max(x - 1, 0); i < Math.min(x + 2, game.rows); i++) {
                for (var j = Math.max(y - 1, 0); j < Math.min(y + 2, game.cols); j++) {
                    if (game.grid[i][j].flagged) {
                        flagNum += 1;
                    }
                }
            }
            console.log(flagNum);
            if (flagNum === game.grid[x][y].neighboorCount) {
                // console.log('雷数相等')
                var failFlag = false;
                for (var i = Math.max(x - 1, 0); i < Math.min(x + 2, game.rows); i++) {
                    for (var j = Math.max(y - 1, 0); j < Math.min(y + 2, game.cols); j++) {
                        if (game.grid[i][j].mine && !game.grid[i][j].flagged) {
                            game.grid[i][j].revealed = true;
                            failFlag = true;
                        }
                        else if (!game.grid[i][j].flagged) {
                            game.grid[i][j].reveal(this, game.grid);
                        }
                    }
                }
                if (failFlag) {
                    game.gameStatus = gameStatus.Fail;
                    game.showAll(gameStatus.Fail);
                }
            }
        }
        return;
    }
    if (event.button === 0) {
        game.mouseChordingHold_2 = false;
        if (game.mouseLeftHold) {
            game.mouseLeftHold = false;
            if (!game.grid[x][y].revealed && !game.grid[x][y].flagged) {
                if (game.gameStatus === gameStatus.NotReady) {
                    game.laymine(x, y);
                    game.gameStatus = gameStatus.Playing;
                }
                if (game.grid[x][y].mine) {
                    game.grid[x][y].revealed = true;
                    game.gameStatus = gameStatus.Fail;
                    game.showAll(gameStatus.Fail);
                    return;
                }
                game.grid[x][y].reveal(this, game.grid);
                game.grid[x][y].hold = false;
                game.grid[x][y].show(this, gameStatus.Playing);
            }
        }
    }
    else {
        game.mouseRightHold = false;
        game.mouseChordingHold_2 = false;
    }
    if (game.isGameWin()) {
        game.showAll(gameStatus.Win);
    }
}
function handleMouseMove(event) {
    event.preventDefault();
    if (game.gameStatus == gameStatus.Win || game.gameStatus == gameStatus.Fail)
        return;
    var rect = this.getBoundingClientRect();
    var y = Math.floor((event.clientX - rect.left) / game.cellWidth);
    var x = Math.floor((event.clientY - rect.top) / game.cellWidth);
    if (game.mouseOldPos[0] === x && game.mouseOldPos[1] === y) {
        return;
    }
    else {
        if (game.mouseLeftHold) {
            game.grid[game.mouseOldPos[0]][game.mouseOldPos[1]].hold = false;
            game.grid[x][y].hold = true;
            game.grid[game.mouseOldPos[0]][game.mouseOldPos[1]].show(this, gameStatus.Playing);
            game.grid[x][y].show(this, gameStatus.Playing);
        }
        else if (game.mouseChordingHold) {
            for (var i = Math.max(game.mouseOldPos[0] - 1, 0); i < Math.min(game.mouseOldPos[0] + 2, game.rows); i++) {
                for (var j = Math.max(game.mouseOldPos[1] - 1, 0); j < Math.min(game.mouseOldPos[1] + 2, game.cols); j++) {
                    game.grid[i][j].hold = false;
                    game.grid[i][j].show(this, gameStatus.Playing);
                }
            }
            for (var i = Math.max(x - 1, 0); i < Math.min(x + 2, game.rows); i++) {
                for (var j = Math.max(y - 1, 0); j < Math.min(y + 2, game.cols); j++) {
                    game.grid[i][j].hold = true;
                    game.grid[i][j].show(this, gameStatus.Playing);
                }
            }
        }
        game.mouseOldPos = [x, y];
    }
}
function handleMouseOut(event) {
    event.preventDefault();
    if (game.gameStatus == gameStatus.Win || game.gameStatus == gameStatus.Fail)
        return;
    var rect = this.getBoundingClientRect();
    var y = Math.floor((event.clientX - rect.left) / game.cellWidth);
    var x = Math.floor((event.clientY - rect.top) / game.cellWidth);
    for (var i = Math.max(game.mouseOldPos[0] - 1, 0); i < Math.min(game.mouseOldPos[0] + 2, game.rows); i++) {
        for (var j = Math.max(game.mouseOldPos[1] - 1, 0); j < Math.min(game.mouseOldPos[1] + 2, game.cols); j++) {
            game.grid[i][j].hold = false;
            game.grid[i][j].show(this, gameStatus.Playing);
        }
    }
    game.mouseChordingHold = false;
    game.mouseChordingHold_2 = false;
    game.mouseLeftHold = false;
    game.mouseRightHold = false;
}
function handleTouch(event) {
    // event.preventDefault();
    // touchEnd = Date.now();
    // const rect = this.getBoundingClientRect();
    // const x = event.targetTouches[0].clientX - rect.left;
    // const y = event.targetTouches[0].clientY - rect.top;
    // if (touchEnd - touchStart > 500) {
    //   for (let i = 0; i < game.cols; i++) {
    //     for (let j = 0; j < game.rows; j++) {
    //       if (game.grid[i][j].contains(x, y)) {
    //         // game.grid[i][j].flag(this);
    //       }
    //     }
    //   }
    // } else {
    //   for (let i = 0; i < game.cols; i++) {
    //     for (let j = 0; j < game.rows; j++) {
    //       if (game.grid[i][j].contains(x, y)) {
    //         if (game.grid[i][j].flagged) {
    //           game.grid[i][j].flagged = false;
    //         }
    //         game.grid[i][j].reveal(this, game.grid);
    //       }
    //     }
    //   }
    // }
    // game.updateGame();
    // // flaggedElement.textContent = String(game.flagged);
    // if (game.gameOver) {
    //   game.showAll();
    //   // flaggedElement.textContent = `Du scoret ${game.score} av ${game.MINENUM} mulige.`;
    // }
}
img_10.onload = function () {
    game.reset();
    game.gameStatus = gameStatus.NotReady;
};
