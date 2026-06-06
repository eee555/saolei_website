export interface PlotPoint {
    x: number;
    y: number;
}

export interface PlotPadding {
    top: number;
    right: number;
    bottom: number;
    left: number;
}

export interface PlotDomain {
    xMin: number;
    xMax: number;
    yMin: number;
    yMax: number;
}

export interface PlotSize {
    width: number;
    height: number;
}

export interface PlotArea {
    x: number;
    y: number;
    width: number;
    height: number;
}

export interface SvgPoint {
    x: number;
    y: number;
}

export const defaultPlotPadding: PlotPadding = {
    top: 12,
    right: 16,
    bottom: 28,
    left: 40,
};

export function getPlotArea(size: PlotSize, padding: PlotPadding = defaultPlotPadding): PlotArea {
    return {
        x: padding.left,
        y: padding.top,
        width: Math.max(0, size.width - padding.left - padding.right),
        height: Math.max(0, size.height - padding.top - padding.bottom),
    };
}

export function createLinearScale(domainMin: number, domainMax: number, rangeMin: number, rangeMax: number) {
    const domainSpan = domainMax - domainMin;

    return (value: number) => {
        if (!Number.isFinite(value)) return rangeMin;
        if (!Number.isFinite(domainSpan) || domainSpan === 0) return (rangeMin + rangeMax) / 2;
        return rangeMin + (value - domainMin) / domainSpan * (rangeMax - rangeMin);
    };
}

export function pointToSvg(point: PlotPoint, domain: PlotDomain, area: PlotArea): SvgPoint {
    const scaleX = createLinearScale(domain.xMin, domain.xMax, area.x, area.x + area.width);
    const scaleY = createLinearScale(domain.yMin, domain.yMax, area.y + area.height, area.y);

    return {
        x: scaleX(point.x),
        y: scaleY(point.y),
    };
}

export function pointsToSvg(points: PlotPoint[], domain: PlotDomain, area: PlotArea): SvgPoint[] {
    return points.filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y)).map((point) => pointToSvg(point, domain, area));
}

export function getDataDomain(points: PlotPoint[], paddingRatio = 0.05): PlotDomain {
    const xs = points.map((point) => point.x).filter(Number.isFinite);
    const ys = points.map((point) => point.y).filter(Number.isFinite);

    return {
        ...padRange(Math.min(...xs), Math.max(...xs), paddingRatio, 0, 1, 'x'),
        ...padRange(Math.min(...ys), Math.max(...ys), paddingRatio, 0, 1, 'y'),
    };
}

export function getNiceTicks(min: number, max: number, count = 5): number[] {
    if (!Number.isFinite(min) || !Number.isFinite(max) || count <= 0) return [];
    if (min === max) return [min];

    const span = niceNumber(max - min, false);
    const step = niceNumber(span / Math.max(1, count - 1), true);
    const tickMin = Math.ceil(min / step) * step;
    const tickMax = Math.floor(max / step) * step;
    const ticks: number[] = [];

    for (let tick = tickMin; tick <= tickMax + step / 2; tick += step) {
        ticks.push(roundToPrecision(tick, step));
    }

    return ticks;
}

export function formatTick(value: number): string {
    if (!Number.isFinite(value)) return '';
    if (Math.abs(value) >= 1000 || Math.abs(value) < 0.001 && value !== 0) return value.toExponential(2);
    return Number(value.toPrecision(6)).toString();
}

function padRange(
    min: number,
    max: number,
    paddingRatio: number,
    fallbackMin: number,
    fallbackMax: number,
    axis: 'x' | 'y',
) {
    const prefix = axis === 'x' ? 'x' : 'y';

    if (!Number.isFinite(min) || !Number.isFinite(max)) {
        return {
            [`${prefix}Min`]: fallbackMin,
            [`${prefix}Max`]: fallbackMax,
        };
    }

    if (min === max) {
        const halfSpan = Math.max(Math.abs(min) * paddingRatio, 1);

        return {
            [`${prefix}Min`]: min - halfSpan,
            [`${prefix}Max`]: max + halfSpan,
        };
    }

    const padding = (max - min) * paddingRatio;

    return {
        [`${prefix}Min`]: min - padding,
        [`${prefix}Max`]: max + padding,
    };
}

function niceNumber(value: number, round: boolean): number {
    const exponent = Math.floor(Math.log10(value));
    const fraction = value / 10 ** exponent;
    let niceFraction = 10;

    if (round) {
        if (fraction < 1.5) niceFraction = 1;
        else if (fraction < 3) niceFraction = 2;
        else if (fraction < 7) niceFraction = 5;
    } else if (fraction <= 1) niceFraction = 1;
    else if (fraction <= 2) niceFraction = 2;
    else if (fraction <= 5) niceFraction = 5;

    return niceFraction * 10 ** exponent;
}

function roundToPrecision(value: number, step: number): number {
    const precision = Math.max(0, -Math.floor(Math.log10(step)) + 2);
    return Number(value.toFixed(precision));
}
