import type { PlotPoint } from '@putianyi888/vue3-plots';

import type { getStat_stat, VideoAbstract } from '@/utils/videoabstract';

export function videoToPlotPoint(video: VideoAbstract, statX: getStat_stat, statY: getStat_stat): PlotPoint<VideoAbstract> | undefined {
    const point = {
        x: video[statX],
        y: video[statY],
        data: video,
    };

    if (isNaN(point.x) || isNaN(point.y)) return undefined;
    return point;
}
