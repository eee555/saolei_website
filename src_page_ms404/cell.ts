let img_0 = new Image();
img_0.src = 'image/10.png';
let img_1 = new Image();
img_1.src = 'image/11.png';
let img_2 = new Image();
img_2.src = 'image/12.png';
let img_3 = new Image();
img_3.src = 'image/13.png';
let img_4 = new Image();
img_4.src = 'image/14.png';
let img_5 = new Image();
img_5.src = 'image/15.png';
let img_6 = new Image();
img_6.src = 'image/16.png';
let img_7 = new Image();
img_7.src = 'image/17.png';
let img_8 = new Image();
img_8.src = 'image/18.png';
let img_10 = new Image();
img_10.src = 'image/00.png';
let img_11 = new Image();
img_11.src = 'image/03.png';
let img_12 = new Image();
img_12.src = 'image/01.png';
let img_13 = new Image();
img_13.src = 'image/02.png';
let img_14 = new Image();
img_14.src = 'image/04.png';
let arr: Array<HTMLImageElement> = [img_0, img_1, img_2, img_3, img_4, img_5, img_6, img_7, img_8];

class Cell {
  mine: boolean;
  revealed: boolean;
  x: number;
  y: number;
  neighboorCount: number;
  flagged: boolean;
  hold: boolean;    // 是否被按住，即是否需要高亮

  constructor(public i: number, public j: number, public w: number) {
    this.flagged = false;
    this.mine = false;
    this.revealed = false;
    this.x = i * this.w;
    this.y = j * this.w;
    this.neighboorCount = 0;
    this.hold = false;
  }

  show(canvas: HTMLCanvasElement, state: gameStatus) {
    // console.log(this.x)
    // console.log(this.y)
    const ctx = <CanvasRenderingContext2D>canvas.getContext('2d');
    if((state === gameStatus.NotReady || state === gameStatus.Playing) && this.hold && !this.flagged && !this.revealed) {
      ctx.drawImage(arr[0], this.y, this.x, this.w, this.w);
      return;
    }
    if(state === gameStatus.NotReady) {
      ctx.drawImage(img_10, this.y, this.x, this.w, this.w);
      return;
    }
    if(this.revealed) {
      if(this.mine) {
        ctx.drawImage(img_13, this.y, this.x, this.w, this.w);
      } else {
        ctx.drawImage(arr[this.neighboorCount], this.y, this.x, this.w, this.w);
      }
    } else {
      if(this.flagged) {
        if(!this.mine && state === gameStatus.Fail) {
          ctx.drawImage(img_14, this.y, this.x, this.w, this.w);
        } else {
          ctx.drawImage(img_11, this.y, this.x, this.w, this.w);
        }
      } else {
        if(this.mine) {
          if(state === gameStatus.Win) {
            ctx.drawImage(img_11, this.y, this.x, this.w, this.w);
          } else if(state === gameStatus.Fail) {
            ctx.drawImage(img_12, this.y, this.x, this.w, this.w);
          } else {
            ctx.drawImage(img_10, this.y, this.x, this.w, this.w);
          }
        } else {
          ctx.drawImage(img_10, this.y, this.x, this.w, this.w);
        }
      }
    }
  }

  countNeighboors(grid: Array<Array<Cell>>) {
    if (this.mine) return;
    let total = 0;
    for (let offsetX = -1; offsetX <= 1; offsetX++) {
      for (let offsetY = -1; offsetY <= 1; offsetY++) {
        const i = this.i + offsetX;
        const j = this.j + offsetY;
        if (!!grid[i] && !!grid[i][j] && grid[i][j].mine) total++;
      }
    }
    this.neighboorCount = total;
  }

  // contains(x: number, y: number) {
  //   return (x > this.x && x < this.x + this.w && y > this.y && y < this.y + this.w)
  // }

  reveal(canvas: HTMLCanvasElement, grid: Array<Array<Cell>>) {
    if (!this.flagged) {
      this.revealed = true;
      if (this.neighboorCount === 0 && !this.mine) this.floodFill(canvas, grid);
      this.show(canvas, gameStatus.Playing);
    }
  }

  floodFill(canvas: HTMLCanvasElement, grid: Array<Array<Cell>>) {
    for (let offsetX = -1; offsetX <= 1; offsetX++) {
      for (let offsetY = -1; offsetY <= 1; offsetY++) {
        const i = this.i + offsetX;
        const j = this.j + offsetY;
        if (!!grid[i] && !!grid[i][j] && !grid[i][j].mine && !grid[i][j].revealed) grid[i][j].reveal(canvas, grid)
      }
    }
  }
}
