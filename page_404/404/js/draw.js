"use strict";
function draw(grid) {
    var canvas = document.querySelector('canvas');
    canvas.height = CANVAS_HEIGHT;
    canvas.width = CANVAS_WIDTH;
    for (var i = 0; i < cols; i++) {
        for (var j = 0; j < rows; j++) {
            grid[i][j].show(canvas);
        }
    }
}
