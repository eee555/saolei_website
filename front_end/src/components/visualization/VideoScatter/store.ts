import { defineStore } from 'pinia';

import { videoToPlotPoint } from './utils';

import { AnyShape, PlotPoint } from '@/components/visualization/Plots';
import { colorTheme, VideoScatterConfig } from '@/store';
import { pinia } from '@/store/create';
import { PiecewiseColorScheme } from '@/utils/colors';
import { getPiecewiseColorSchemeName, MS_Level } from '@/utils/ms_const';
import { VideoAbstract } from '@/utils/videoabstract';

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
    state: () => ({
        rawData: [] as VideoAbstract[],
        canvasMode: '' as '' | 'select',
        selectionMode: 'assign' as 'assign' | 'union' | 'diff' | 'intersect',
        selectedFlags: [] as boolean[],
    }),
    getters: {
        scatterData() {
            // 返回值
            const indices = [] as number[];
            const points = [] as PlotPoint<VideoAbstract>[];
            const colors = [] as string[];

            // 生成颜色计算函数
            let colorHandle: (video: VideoAbstract) => string;
            const colorBy = VideoScatterConfig.value.colorBy;
            if (colorBy === 'level') {
                colorHandle = (video: VideoAbstract) => colorTheme.value.level[video.level];
            } else if (colorBy === 'time') {
                const schemes = {
                    b: getTimeColorScheme('b'),
                    i: getTimeColorScheme('i'),
                    e: getTimeColorScheme('e'),
                };
                colorHandle = (video: VideoAbstract) => schemes[video.level].getColor(video.time);
            } else {
                const name = getPiecewiseColorSchemeName(colorBy);
                const scheme = new PiecewiseColorScheme(colorTheme.value[name].colors, colorTheme.value[name].thresholds);
                colorHandle = (video: VideoAbstract) => scheme.getColor(video.getStat(colorBy)!);
            }

            for (let i = 0; i < this.rawData.length; i++) {
                if (VideoScatterConfig.value.showOnlySelected && !this.selectedFlags[i]) continue;
                const video = this.rawData[i];
                const point = videoToPlotPoint(video, VideoScatterConfig.value.x, VideoScatterConfig.value.y);
                if (point === undefined) continue;

                points.push(point);
                colors.push(colorHandle(video));
                indices.push(i);
            }

            return { indices, points, colors };
        },
    },
    actions: {
        setRawData(data: VideoAbstract[]) {
            this.rawData = data;
            this.selectedFlags = Array(data.length).fill(false);
        },
        selectionDraw(shape: AnyShape) {
            switch (VideoScatterStore.selectionMode) {
                case 'assign': {
                    // if contains, true, else, false
                    for (let i = 0; i < this.rawData.length; i++) {
                        VideoScatterStore.selectedFlags[i] = inShape(this.rawData[i], shape);
                    }
                    break;
                }
                case 'union': {
                    // if contains, true, else, do nothing
                    for (let i = 0; i < this.rawData.length; i++) {
                        if (inShape(this.rawData[i], shape)) VideoScatterStore.selectedFlags[i] = true;
                    }
                    break;
                }
                case 'diff': {
                    // if contains, false, else, do nothing
                    for (let i = 0; i < this.rawData.length; i++) {
                        if (inShape(this.rawData[i], shape)) VideoScatterStore.selectedFlags[i] = false;
                    }
                    break;
                }
                case 'intersect': {
                    // if contains, do nothing, else, false
                    for (let i = 0; i < this.rawData.length; i++) {
                        if (!inShape(this.rawData[i], shape)) VideoScatterStore.selectedFlags[i] = false;
                    }
                }
            }
        },
    },
})(pinia);
