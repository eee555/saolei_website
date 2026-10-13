import { Line } from '@putianyi888/vue3-plots';
import { describe, expect, it } from 'vitest';
import { createSSRApp, h } from 'vue';
import { renderToString } from 'vue/server-renderer';

import { counterValue } from './counter';
import type { PreparedCounter } from './counter';
import { timelinePoints } from './timeline';

describe('timeline line sampling', () => {
    it('uses the upstream SVG sampling to retain adjacent extrema without changing precise counter values', async () => {
        const samples = Array.from({ length: 100001 }, (_, index) => ({ timeMs: index, eventIndex: index, value: index === 50000 ? 95 : index === 50001 ? -95 : 0 }));
        const counter: PreparedCounter = { samples, formatter: String, error: '' };
        const points = timelinePoints(counter, 100000);
        const svg = await renderToString(createSSRApp({ render: () => h(Line, { points,
            domain: { xMin: 0, xMax: 100000, yMin: -100, yMax: 100 },
            size: { width: 320, height: 160 },
            padding: { top: 0, bottom: 0, left: 0, right: 0 },
            sampling: 'min-max' }) }));
        const path = (/<path[^>]*\bd="([^"]*)"/u).exec(svg)?.[1] ?? '';
        const vertices = [...path.matchAll(/[ML] ([\d.+-]+) ([\d.+-]+)/gu)];
        expect(vertices.length).toBeGreaterThan(0);
        expect(vertices.length).toBeLessThanOrEqual(4 * 321);
        expect(vertices.some((vertex) => Number(vertex[2]) === 4)).toBe(true);
        expect(vertices.some((vertex) => Number(vertex[2]) === 156)).toBe(true);
        expect(points).toHaveLength(100001);
        expect(counter.samples).toBe(samples);
        expect(counterValue(samples, 50000)).toBe(95);
        expect(counterValue(samples, 50001)).toBe(-95);
        expect(counterValue(samples, 50000.5)).toBe(0);
    });
});
