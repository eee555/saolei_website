"use strict";
// 主要定义了局面整体
var Game = /** @class */ (function () {
    function Game(canvas, ROW, COLUMN, MINENUM, SIZE) {
        this.canvas = canvas;
        this.ROW = ROW;
        this.COLUMN = COLUMN;
        this.MINENUM = MINENUM;
        this.SIZE = SIZE;
        this.gameStatus = gameStatus.NotReady;
        this.flagged = 0;
        this.cellsLeft = Infinity;
        this.cellWidth = SIZE;
        this.cols = COLUMN;
        this.rows = ROW;
        this.options = [];
        var grid = make2dArray(this.rows, this.cols);
        for (var i = 0; i < this.rows; i++) {
            for (var j = 0; j < this.cols; j++) {
                grid[i][j] = new Cell(i, j, this.cellWidth);
            }
        }
        this.grid = grid;
        this.score = 0;
        this.mouseLeftHold = false;
        this.mouseRightHold = false;
        this.mouseChordingHold = false; // 这两个标志与按下后的高亮有关
        this.mouseChordingHold_2 = false; // 双击后抬起一个键的状态
        this.mouseOldPos = [0, 0]; // 鼠标的上一个位置
    }
    Game.prototype.reset = function () {
        this.options = [];
        for (var i = 0; i < this.rows; i++) {
            for (var j = 0; j < this.cols; j++) {
                this.grid[i][j].revealed = false;
                this.grid[i][j].flagged = false;
                this.grid[i][j].mine = false;
                this.grid[i][j].hold = false;
                this.grid[i][j].neighboorCount = 0;
                this.grid[i][j].show(this.canvas, gameStatus.NotReady);
            }
        }
        this.mouseLeftHold = false;
        this.mouseRightHold = false;
        this.mouseChordingHold = false;
        this.mouseChordingHold_2 = false;
    };
    Game.prototype.laymine = function (x, y) {
        for (var i = 0; i < this.rows; i++) {
            for (var j = 0; j < this.cols; j++) {
                if (i !== x || j !== y) {
                    this.options.push([i, j]);
                }
            }
        }
        for (var n = 0; n < this.MINENUM; n++) {
            var index = Math.floor(Math.random() * (this.options.length));
            var _a = this.options.splice(index, 1)[0], i = _a[0], j = _a[1];
            this.grid[i][j].mine = true;
            // console.log('dfd')
        }
        for (var i = 0; i < this.rows; i++) {
            for (var j = 0; j < this.cols; j++) {
                this.grid[i][j].countNeighboors(this.grid);
            }
        }
    };
    Game.prototype.isGameWin = function () {
        for (var i = 0; i < this.rows; i++) {
            for (var j = 0; j < this.cols; j++) {
                if (!this.grid[i][j].mine && !this.grid[i][j].revealed) {
                    return false;
                }
            }
        }
        this.gameStatus = gameStatus.Win;
        return true;
    };
    Game.prototype.showAll = function (state) {
        this.mouseLeftHold = false;
        this.mouseRightHold = false;
        this.mouseChordingHold = false;
        this.mouseChordingHold_2 = false;
        for (var i = 0; i < this.rows; i++) {
            for (var j = 0; j < this.cols; j++) {
                var cell = this.grid[i][j];
                if (cell.mine) {
                    cell.show(this.canvas, state);
                }
            }
        }
    };
    return Game;
}());
