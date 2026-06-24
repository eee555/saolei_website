export interface Point {
    x: number;
    y: number;
}

export type ShapeType = 'rect' | 'ellipse';

export abstract class Shape<TType extends ShapeType> {
    abstract readonly type: TType;

    abstract contains(point: Point): boolean;
}

export class Rect extends Shape<'rect'> {
    readonly type = 'rect';

    constructor(
        readonly x: number,
        readonly y: number,
        readonly width: number,
        readonly height: number,
    ) {
        super();
    }

    contains(point: Point): boolean {
        return point.x >= this.x
            && point.x <= this.x + this.width
            && point.y >= this.y
            && point.y <= this.y + this.height;
    }
}

export class Ellipse extends Shape<'ellipse'> {
    readonly type = 'ellipse';

    constructor(
        readonly cx: number,
        readonly cy: number,
        readonly rx: number,
        readonly ry: number,
    ) {
        super();
    }

    contains(point: Point): boolean {
        if (this.rx <= 0 || this.ry <= 0) return false;

        const dx = (point.x - this.cx) / this.rx;
        const dy = (point.y - this.cy) / this.ry;

        return dx * dx + dy * dy <= 1;
    }
}

export type AnyShape = Rect | Ellipse;
