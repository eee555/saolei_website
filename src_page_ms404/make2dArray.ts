function make2dArray(rows: number, cols: number) {
  const arr = new Array(cols);
  for (let i = 0; i < cols; i++) {
    arr[i] = new Array(rows);
  }
  return arr
}

enum gameStatus {
  NotReady,
  Playing,
  Win,
  Fail,
}
