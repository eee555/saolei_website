import { MS_Software } from '@/utils/ms_const';
import { getStat_stat, VideoAbstract } from '@/utils/videoabstract';

interface SortOption {
    softwareFilter: Array<MS_Software>;
    sortDesc: boolean;
    sortBy: getStat_stat;
}

export function getBest(videos: Array<VideoAbstract>, option: SortOption) {
    let bestValue = NaN;
    let bestIndex = -1;
    videos.forEach((video, index) => {
        if (!option.softwareFilter!.includes(video.software)) return;
        const thisValue = video.getStat(option.sortBy!);
        if (thisValue === undefined) return {
            bestValue: NaN,
            bestIndex: -1,
        };
        if (
            isNaN(bestValue) ||
            thisValue > bestValue && option.sortDesc ||
            thisValue < bestValue && !option.sortDesc
        ) {
            bestValue = thisValue;
            bestIndex = index;
        }
    });
    return { bestValue, bestIndex };
}
