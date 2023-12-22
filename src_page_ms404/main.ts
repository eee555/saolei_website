// const slider = <HTMLInputElement>document.querySelector('#mines');
// let numberOfMines = slider.value;
const canvas = <HTMLCanvasElement>document.querySelector('canvas');
const flaggedElement = <HTMLTitleElement>document.getElementById('flagged');
const restartButton = <HTMLButtonElement>document.querySelector('#restart');

const SIZE: number = 16; // 方格边长
const ROW: number = 32;
const COLUMN: number = 48;
const CANVAS_HEIGHT: number = SIZE * ROW;
const CANVAS_WIDTH: number = SIZE * COLUMN;
const MINENUM: number = 404;

canvas.height = CANVAS_HEIGHT;
canvas.width = CANVAS_WIDTH;
let game = new Game(canvas, ROW, COLUMN, MINENUM, SIZE);

restartButton.addEventListener('click', () => { game.reset(); game.gameStatus = gameStatus.NotReady; });

canvas.oncontextmenu = () => false; // 关闭右键菜单
canvas.addEventListener('mousedown', handleClickDown);
canvas.addEventListener('mouseup', handleClickUp);
canvas.addEventListener('mousemove', handleMouseMove);
canvas.addEventListener('mouseout', handleMouseOut);

let touchStart = 0;
let touchEnd = 0;

canvas.addEventListener('touchend', handleTouch);
canvas.addEventListener('touchstart', (e) => {
  e.preventDefault();
  touchStart = Date.now();
})

function handleClickDown(this: HTMLCanvasElement, event: MouseEvent) {
  event.preventDefault();
  if (game.gameStatus == gameStatus.Win || game.gameStatus == gameStatus.Fail) return;
  const rect = this.getBoundingClientRect();
  const y = Math.floor((event.clientX - rect.left) / game.cellWidth);
  const x = Math.floor((event.clientY - rect.top) / game.cellWidth);
  if (game.mouseRightHold || game.mouseLeftHold || game.mouseChordingHold_2) {
    game.mouseChordingHold = true;
    // console.log('把双击标志设为真')
    game.mouseRightHold = false;
    game.mouseLeftHold = false;
    game.mouseChordingHold_2 = false;
    for (let i = Math.max(x - 1, 0); i < Math.min(x + 2, game.rows); i++) {
      for (let j = Math.max(y - 1, 0); j < Math.min(y + 2, game.cols); j++) {
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
  } else if (event.button === 2) {
    game.mouseRightHold = true;
    if (!game.grid[x][y].revealed) {
      game.grid[x][y].flagged = !game.grid[x][y].flagged;
      game.grid[x][y].show(this, gameStatus.Playing);
    }
  }
};

function handleClickUp(this: HTMLCanvasElement, event: MouseEvent) {
  event.preventDefault();
  if (game.gameStatus == gameStatus.Win || game.gameStatus == gameStatus.Fail) return;
  const rect = this.getBoundingClientRect();
  const y = Math.floor((event.clientX - rect.left) / game.cellWidth);
  const x = Math.floor((event.clientY - rect.top) / game.cellWidth);
  if (game.mouseChordingHold) {
    game.mouseChordingHold = false;
    game.mouseChordingHold_2 = true;
    // console.log('双击回调')
    for (let i = Math.max(x - 1, 0); i < Math.min(x + 2, game.rows); i++) {
      for (let j = Math.max(y - 1, 0); j < Math.min(y + 2, game.cols); j++) {
        game.grid[i][j].hold = false;
        game.grid[i][j].show(this, gameStatus.Playing);
      }
    }
    // console.log('双击回调2')
    if (game.grid[x][y].revealed) {
      let flagNum = 0;
      for (let i = Math.max(x - 1, 0); i < Math.min(x + 2, game.rows); i++) {
        for (let j = Math.max(y - 1, 0); j < Math.min(y + 2, game.cols); j++) {
          if (game.grid[i][j].flagged) {
            flagNum += 1;
          }
        }
      }
      console.log(flagNum)
      if (flagNum === game.grid[x][y].neighboorCount) {
        // console.log('雷数相等')
        let failFlag = false;
        for (let i = Math.max(x - 1, 0); i < Math.min(x + 2, game.rows); i++) {
          for (let j = Math.max(y - 1, 0); j < Math.min(y + 2, game.cols); j++) {
            if (game.grid[i][j].mine && !game.grid[i][j].flagged) {
              game.grid[i][j].revealed = true;
              failFlag = true;
            } else if (!game.grid[i][j].flagged) {
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
  } else {
    game.mouseRightHold = false;
    game.mouseChordingHold_2 = false;
  }
  if (game.isGameWin()) {
    game.showAll(gameStatus.Win);
  }
}

function handleMouseMove(this: HTMLCanvasElement, event: MouseEvent) {
  event.preventDefault();
  if (game.gameStatus == gameStatus.Win || game.gameStatus == gameStatus.Fail) return;
  const rect = this.getBoundingClientRect();
  const y = Math.floor((event.clientX - rect.left) / game.cellWidth);
  const x = Math.floor((event.clientY - rect.top) / game.cellWidth);
  if (game.mouseOldPos[0] === x && game.mouseOldPos[1] === y) {
    return;
  } else {
    if (game.mouseLeftHold) {
      game.grid[game.mouseOldPos[0]][game.mouseOldPos[1]].hold = false;
      game.grid[x][y].hold = true;
      game.grid[game.mouseOldPos[0]][game.mouseOldPos[1]].show(this, gameStatus.Playing);
      game.grid[x][y].show(this, gameStatus.Playing);
    } else if (game.mouseChordingHold) {
      for (let i = Math.max(game.mouseOldPos[0] - 1, 0); i < Math.min(game.mouseOldPos[0] + 2, game.rows); i++) {
        for (let j = Math.max(game.mouseOldPos[1] - 1, 0); j < Math.min(game.mouseOldPos[1] + 2, game.cols); j++) {
          game.grid[i][j].hold = false;
          game.grid[i][j].show(this, gameStatus.Playing);
        }
      }
      for (let i = Math.max(x - 1, 0); i < Math.min(x + 2, game.rows); i++) {
        for (let j = Math.max(y - 1, 0); j < Math.min(y + 2, game.cols); j++) {
          game.grid[i][j].hold = true;
          game.grid[i][j].show(this, gameStatus.Playing);
        }
      }
    }
    game.mouseOldPos = [x, y];
  }
}

function handleMouseOut(this: HTMLCanvasElement, event: MouseEvent) {
  event.preventDefault();
  if (game.gameStatus == gameStatus.Win || game.gameStatus == gameStatus.Fail) return;
  const rect = this.getBoundingClientRect();
  const y = Math.floor((event.clientX - rect.left) / game.cellWidth);
  const x = Math.floor((event.clientY - rect.top) / game.cellWidth);
  for (let i = Math.max(game.mouseOldPos[0] - 1, 0); i < Math.min(game.mouseOldPos[0] + 2, game.rows); i++) {
    for (let j = Math.max(game.mouseOldPos[1] - 1, 0); j < Math.min(game.mouseOldPos[1] + 2, game.cols); j++) {
      game.grid[i][j].hold = false;
      game.grid[i][j].show(this, gameStatus.Playing);
    }
  }
  game.mouseChordingHold = false;
  game.mouseChordingHold_2 = false;
  game.mouseLeftHold = false;
  game.mouseRightHold = false;
}

function handleTouch(this: HTMLCanvasElement, event: TouchEvent) {
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
img_10.onload = function () { // 等未打开的图加载完以后再初始化游戏
  game.reset();
  game.gameStatus = gameStatus.NotReady;
}



