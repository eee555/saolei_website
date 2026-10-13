import tinycolor from 'tinycolor2';

import { ArrayUtils } from '@/utils/arrays';
import type { PiecewiseColorSchemeInterface } from '@/utils/colors';

export function colorSchemeError(value: unknown, min = -Infinity, max = Infinity): string | null {
    if (typeof value !== 'object' || value === null || !('thresholds' in value) || !('colors' in value)) return 'invalidShape';
    const { thresholds, colors } = value;
    if (!Array.isArray(thresholds) || !Array.isArray(colors) || colors.length !== thresholds.length + 1) return 'invalidShape';
    if (!thresholds.every((threshold: unknown) => typeof threshold === 'number' && Number.isFinite(threshold) && threshold >= min && threshold <= max)) return 'invalidThresholds';
    if (!ArrayUtils.isAscending(thresholds as number[]) && !ArrayUtils.isDescending(thresholds as number[])) return 'unsortedThresholds';
    if (!colors.every((color: unknown) => typeof color === 'string' && tinycolor(color).isValid())) return 'invalidColors';
    return null;
}

export function parseColorScheme(json: string, min = -Infinity, max = Infinity): PiecewiseColorSchemeInterface {
    const value: unknown = JSON.parse(json);
    const error = colorSchemeError(value, min, max);
    if (error !== null) throw new Error(error);
    const { colors, thresholds } = value as PiecewiseColorSchemeInterface;
    return { colors: [...colors], thresholds: [...thresholds] };
}

export function colorSchemeIntervals(scheme: PiecewiseColorSchemeInterface, min = -Infinity, max = Infinity): { index: number; color: string; lower: number; upper: number; lowerClosed: boolean; upperClosed: boolean }[] {
    const ascending = ArrayUtils.isAscending(scheme.thresholds);
    return scheme.colors.map((color, index) => {
        const previous = scheme.thresholds[index - 1];
        const next = scheme.thresholds[index];
        return {
            index,
            color,
            lower: ascending ? previous ?? min : next ?? min,
            upper: ascending ? next ?? max : previous ?? max,
            lowerClosed: ascending ? previous === undefined && Number.isFinite(min) : next !== undefined || Number.isFinite(min),
            upperClosed: ascending ? next !== undefined || Number.isFinite(max) : previous === undefined && Number.isFinite(max),
        };
    });
}

export function splitColorScheme(scheme: PiecewiseColorSchemeInterface, index: number, min = -Infinity, max = Infinity): PiecewiseColorSchemeInterface | null {
    const interval = colorSchemeIntervals(scheme, min, max)[index];
    if (interval === undefined) return null;
    const { lower, upper, color } = interval;
    const thresholds = [...scheme.thresholds];
    const span = thresholds.length > 1 ? Math.abs(thresholds[0] - thresholds[thresholds.length - 1]) || 1 : 1;
    const point = Number.isFinite(lower) && Number.isFinite(upper)
        ? lower / 2 + upper / 2
        : Number.isFinite(lower) ? lower + span : Number.isFinite(upper) ? upper - span : 0;
    if (!Number.isFinite(point) || point <= lower || point >= upper) return null;
    thresholds.splice(index, 0, point);
    const colors = [...scheme.colors];
    colors.splice(index + 1, 0, color);
    return { colors, thresholds };
}

export function removeColorSchemeThreshold(scheme: PiecewiseColorSchemeInterface, index: number): PiecewiseColorSchemeInterface {
    const thresholds = [...scheme.thresholds];
    const colors = [...scheme.colors];
    thresholds.splice(index, 1);
    colors.splice(index + 1, 1);
    return { thresholds, colors };
}
