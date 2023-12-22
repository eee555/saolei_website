"use strict";
function restart(canvas, ROW, COLUMN, MINENUM, SIZE) {
    game = new Game(canvas, ROW, COLUMN, MINENUM, SIZE);
    game.start();
}
