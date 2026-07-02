import type { AnyShape, PlotDomain, PlotPadding, PlotPoint, PlotSize } from '@putianyi888/vue3-plots';
import { getDataDomain } from '@putianyi888/vue3-plots';
import { defineStore } from 'pinia';

import { videoToPlotPoint } from './utils';

import { colorTheme, VideoScatterConfig } from '@/store';
import { pinia } from '@/store/create';
import { PiecewiseColorScheme } from '@/utils/colors';
import type { MS_Level } from '@/utils/ms_const';
import { getPiecewiseColorSchemeName, isStandardLevel } from '@/utils/ms_const';
import type { VideoAbstract } from '@/utils/videoabstract';

function inShape(video: VideoAbstract, shape: AnyShape) {
    const point = videoToPlotPoint(video, VideoScatterConfig.value.x, VideoScatterConfig.value.y);
    if (point === undefined) return false;
    return shape.contains(point);
}

function getTimeColorScheme(level: MS_Level) {
    const name = getPiecewiseColorSchemeName('time', level);
    return new PiecewiseColorScheme(colorTheme.value[name].colors, colorTheme.value[name].thresholds);
}

export const VideoScatterStore = defineStore('video-scatter-store', {
    /* eslint-disable @typescript-eslint/no-unnecessary-type-assertion */
    state: () => ({
        rawData: [] as VideoAbstract[],
        canvasMode: '' as '' | 'select',
        selectionMode: 'assign' as 'assign' | 'union' | 'diff' | 'intersect',
        selectedFlags: [] as boolean[],
        plotSize: { width: 640, height: 360 } as PlotSize,
        plotPadding: { top: 12, right: 16, bottom: 42, left: 52 } as PlotPadding,
    }),
    /* eslint-enable @typescript-eslint/no-unnecessary-type-assertion */
    getters: {
        colorHandle() {
            const { colorBy } = VideoScatterConfig.value;

            if (colorBy === 'level') {
                return (video: VideoAbstract) => isStandardLevel(video.level) ? colorTheme.value.level[video.level] : colorTheme.value.level.e;
            } else if (colorBy === 'time') {
                const schemes = {
                    b: getTimeColorScheme('b'),
                    i: getTimeColorScheme('i'),
                    e: getTimeColorScheme('e'),
                };
                return (video: VideoAbstract) => isStandardLevel(video.level) ? schemes[video.level].getColor(video.time) : colorTheme.value.level.e;
            } else {
                const name = getPiecewiseColorSchemeName(colorBy);
                const scheme = new PiecewiseColorScheme(colorTheme.value[name].colors, colorTheme.value[name].thresholds);
                return (video: VideoAbstract) => scheme.getColor(video.getStat(colorBy));
            }
        },
        scatterData() {
            const indices = [] as number[];
            const points = [] as PlotPoint<VideoAbstract>[];

            for (let i = 0; i < this.rawData.length; i++) {
                if (VideoScatterConfig.value.showOnlySelected && !this.selectedFlags[i]) continue;
                const video = this.rawData[i];
                const point = videoToPlotPoint(video, VideoScatterConfig.value.x, VideoScatterConfig.value.y);
                if (point === undefined) continue;

                points.push(point);
                indices.push(i);
            }

            return { indices, points };
        },
        plotDomain(): PlotDomain {
            return getDataDomain(this.scatterData.points);
        },
        fillColor(): string[] {
            return this.scatterData.points.map((point) => this.colorHandle(point.data));
        },
        fillOpacity(): number | number[] {
            if (this.canvasMode === 'select') {
                return this.scatterData.indices.map((index) => (this.selectedFlags[index] ? 1 : 0.7));
            } else {
                return 0.7;
            }
        },
        strokeWidth(): number | number[] {
            if (!VideoScatterConfig.value.highlightSelected) return 0;
            return this.scatterData.indices.map((index) => (this.selectedFlags[index] ? 1 : 0));
        },
        strokeOpacity() {
            return 0.5;
        },
    },
    actions: {
        setRawData(data: VideoAbstract[]) {
            this.rawData = data;
            this.selectedFlags = Array(data.length).fill(true);
        },
        selectionDraw(shape: AnyShape) {
            switch (this.selectionMode) {
                case 'assign': {
                    // if contains, true, else, false
                    for (let i = 0; i < this.rawData.length; i++) {
                        this.selectedFlags[i] = inShape(this.rawData[i], shape);
                    }
                    break;
                }
                case 'union': {
                    // if contains, true, else, do nothing
                    for (let i = 0; i < this.rawData.length; i++) {
                        if (inShape(this.rawData[i], shape)) this.selectedFlags[i] = true;
                    }
                    break;
                }
                case 'diff': {
                    // if contains, false, else, do nothing
                    for (let i = 0; i < this.rawData.length; i++) {
                        if (inShape(this.rawData[i], shape)) this.selectedFlags[i] = false;
                    }
                    break;
                }
                case 'intersect': {
                    // if contains, do nothing, else, false
                    for (let i = 0; i < this.rawData.length; i++) {
                        if (!inShape(this.rawData[i], shape)) this.selectedFlags[i] = false;
                    }
                }
            }
        },
    },
})(pinia);
