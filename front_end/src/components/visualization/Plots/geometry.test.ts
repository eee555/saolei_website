import { describe, expect, it } from 'vitest';

import { Ellipse, Rect } from './geometry';

describe('geometry', () => {
    describe('Rect', () => {
        it('contains points inside and on the boundary', () => {
            const rect = new Rect(10, 20, 30, 40);

            expect(rect.type).toBe('rect');
            expect(rect.contains({ x: 10, y: 20 })).toBe(true);
            expect(rect.contains({ x: 25, y: 40 })).toBe(true);
            expect(rect.contains({ x: 40, y: 60 })).toBe(true);
        });

        it('rejects points outside the rectangle', () => {
            const rect = new Rect(10, 20, 30, 40);

            expect(rect.contains({ x: 9, y: 20 })).toBe(false);
            expect(rect.contains({ x: 41, y: 60 })).toBe(false);
            expect(rect.contains({ x: 10, y: 19 })).toBe(false);
            expect(rect.contains({ x: 40, y: 61 })).toBe(false);
        });
    });

    describe('Ellipse', () => {
        it('contains points inside and on the boundary', () => {
            const ellipse = new Ellipse(10, 20, 6, 4);

            expect(ellipse.type).toBe('ellipse');
            expect(ellipse.contains({ x: 10, y: 20 })).toBe(true);
            expect(ellipse.contains({ x: 16, y: 20 })).toBe(true);
            expect(ellipse.contains({ x: 10, y: 24 })).toBe(true);
            expect(ellipse.contains({ x: 13, y: 22 })).toBe(true);
        });

        it('rejects points outside the ellipse', () => {
            const ellipse = new Ellipse(10, 20, 6, 4);

            expect(ellipse.contains({ x: 17, y: 20 })).toBe(false);
            expect(ellipse.contains({ x: 10, y: 25 })).toBe(false);
            expect(ellipse.contains({ x: 15, y: 24 })).toBe(false);
        });

        it('rejects all points when either radius is not positive', () => {
            expect(new Ellipse(10, 20, 0, 4).contains({ x: 10, y: 20 })).toBe(false);
            expect(new Ellipse(10, 20, 6, 0).contains({ x: 10, y: 20 })).toBe(false);
        });
    });
});
