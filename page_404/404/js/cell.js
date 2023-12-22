"use strict";
var img_0 = new Image();
img_0.src = 'image/10.png';
var img_1 = new Image();
img_1.src = 'image/11.png';
var img_2 = new Image();
img_2.src = 'image/12.png';
var img_3 = new Image();
img_3.src = 'image/13.png';
var img_4 = new Image();
img_4.src = 'image/14.png';
var img_5 = new Image();
img_5.src = 'image/15.png';
var img_6 = new Image();
img_6.src = 'image/16.png';
var img_7 = new Image();
img_7.src = 'image/17.png';
var img_8 = new Image();
img_8.src = 'image/18.png';
var img_10 = new Image();
img_10.src = 'image/00.png';
var img_11 = new Image();
img_11.src = 'image/03.png';
var img_12 = new Image();
img_12.src = 'image/01.png';
var img_13 = new Image();
img_13.src = 'image/02.png';
var img_14 = new Image();
img_14.src = 'image/04.png';
var arr = [img_0, img_1, img_2, img_3, img_4, img_5, img_6, img_7, img_8];
var Cell = /** @class */ (function () {
    function Cell(i, j, w) {
        this.i = i;
        this.j = j;
        this.w = w;
        this.flagged = false;
        this.mine = false;
        this.revealed = false;
        this.x = i * this.w;
        this.y = j * this.w;
        this.neighboorCount = 0;
        this.hold = false;
    }
    Cell.prototype.show = function (canvas, state) {
        // console.log(this.x)
        // console.log(this.y)
        var ctx = canvas.getContext('2d');
        if ((state === gameStatus.NotReady || state === gameStatus.Playing) && this.hold && !this.flagged && !this.revealed) {
            ctx.drawImage(arr[0], this.y, this.x, this.w, this.w);
            return;
        }
        if (state === gameStatus.NotReady) {
            ctx.drawImage(img_10, this.y, this.x, this.w, this.w);
            return;
        }
        if (this.revealed) {
            if (this.mine) {
                ctx.drawImage(img_13, this.y, this.x, this.w, this.w);
            }
            else {
                ctx.drawImage(arr[this.neighboorCount], this.y, this.x, this.w, this.w);
            }
        }
        else {
            if (this.flagged) {
                if (!this.mine && state === gameStatus.Fail) {
                    ctx.drawImage(img_14, this.y, this.x, this.w, this.w);
                }
                else {
                    ctx.drawImage(img_11, this.y, this.x, this.w, this.w);
                }
            }
            else {
                if (this.mine) {
                    if (state === gameStatus.Win) {
                        ctx.drawImage(img_11, this.y, this.x, this.w, this.w);
                    }
                    else if (state === gameStatus.Fail) {
                        ctx.drawImage(img_12, this.y, this.x, this.w, this.w);
                    }
                    else {
                        ctx.drawImage(img_10, this.y, this.x, this.w, this.w);
                    }
                }
                else {
                    ctx.drawImage(img_10, this.y, this.x, this.w, this.w);
                }
            }
        }
    };
    Cell.prototype.countNeighboors = function (grid) {
        if (this.mine)
            return;
        var total = 0;
        for (var offsetX = -1; offsetX <= 1; offsetX++) {
            for (var offsetY = -1; offsetY <= 1; offsetY++) {
                var i = this.i + offsetX;
                var j = this.j + offsetY;
                if (!!grid[i] && !!grid[i][j] && grid[i][j].mine)
                    total++;
            }
        }
        this.neighboorCount = total;
    };
    // contains(x: number, y: number) {
    //   return (x > this.x && x < this.x + this.w && y > this.y && y < this.y + this.w)
    // }
    Cell.prototype.reveal = function (canvas, grid) {
        if (!this.flagged) {
            this.revealed = true;
            if (this.neighboorCount === 0 && !this.mine)
                this.floodFill(canvas, grid);
            this.show(canvas, gameStatus.Playing);
        }
    };
    Cell.prototype.floodFill = function (canvas, grid) {
        for (var offsetX = -1; offsetX <= 1; offsetX++) {
            for (var offsetY = -1; offsetY <= 1; offsetY++) {
                var i = this.i + offsetX;
                var j = this.j + offsetY;
                if (!!grid[i] && !!grid[i][j] && !grid[i][j].mine && !grid[i][j].revealed)
                    grid[i][j].reveal(canvas, grid);
            }
        }
    };
    return Cell;
}());
