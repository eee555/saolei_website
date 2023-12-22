
// 主要定义了局面整体

class Game {
  flagged: number;
  cellsLeft: number;
  grid: Array<Array<Cell>>;
  cellWidth: number;
  cols: number;
  rows: number;
  options: Array<Array<number>>;
  score: number;
  gameStatus: gameStatus;
  mouseLeftHold: Boolean;
  mouseRightHold: Boolean;
  mouseChordingHold: Boolean;  // 这两个标志与按下后的高亮有关
  mouseChordingHold_2: Boolean;// 双击后抬起一个键的状态
  mouseOldPos: Array<number>;       // 鼠标的上一个位置

  constructor(public canvas: HTMLCanvasElement, public ROW: number, public COLUMN: number, public MINENUM: number, public SIZE: number) {
    this.gameStatus = gameStatus.NotReady;
    this.flagged = 0;
    this.cellsLeft = Infinity;
    this.cellWidth = SIZE;
    this.cols = COLUMN;
    this.rows = ROW;
    this.options = [];
    const grid = make2dArray(this.rows, this.cols);
    for (let i = 0; i < this.rows; i++) {
      for (let j = 0; j < this.cols; j++) {
        grid[i][j] = new Cell(i, j, this.cellWidth);
      }
    }
    this.grid = grid;
    this.score = 0;
    this.mouseLeftHold = false;
    this.mouseRightHold = false;
    this.mouseChordingHold = false;  // 这两个标志与按下后的高亮有关
    this.mouseChordingHold_2 = false;// 双击后抬起一个键的状态
    this.mouseOldPos = [0, 0];       // 鼠标的上一个位置
  }
  reset() {
    this.options = [];
    for (let i = 0; i < this.rows; i++) {
      for (let j = 0; j < this.cols; j++) {
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
  }
  laymine(x: number, y: number) {
    for (let i = 0; i < this.rows; i++) {
      for (let j = 0; j < this.cols; j++) {
        if (i !== x || j !== y) {
          this.options.push([i, j]);
        }
      }
    }
    for (let n = 0; n < this.MINENUM; n++) {
      const index = Math.floor(Math.random() * (this.options.length));
      const [i, j] = this.options.splice(index, 1)[0];
      this.grid[i][j].mine = true;
      // console.log('dfd')
    }
    for (let i = 0; i < this.rows; i++) {
      for (let j = 0; j < this.cols; j++) {
        this.grid[i][j].countNeighboors(this.grid);
      }
    }
  }

  isGameWin() {
    for (let i = 0; i < this.rows; i++) {
      for (let j = 0; j < this.cols; j++) {
        if (!this.grid[i][j].mine && !this.grid[i][j].revealed) {
          return false;
        }
      }
    }
    this.gameStatus = gameStatus.Win;
    return true;
  }

  showAll(state: gameStatus) {
    this.mouseLeftHold = false;
    this.mouseRightHold = false;
    this.mouseChordingHold = false;
    this.mouseChordingHold_2 = false;
    for (let i = 0; i < this.rows; i++) {
      for (let j = 0; j < this.cols; j++) {
        const cell = this.grid[i][j];
        if (cell.mine) {
          cell.show(this.canvas, state);
        }
      }
    }
  }
}



