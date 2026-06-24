import type { MS_Software } from '@/utils/ms_const';
import type { getStat_stat, VideoAbstract } from '@/utils/videoabstract';

interface SortOption {
    softwareFilter: MS_Software[];
    sortDesc: boolean;
    sortBy: getStat_stat;
}

export function getBest(videos: VideoAbstract[], option: SortOption): {
    bestValue: number;
    bestIndex: number;
} | undefined {
    let bestValue = NaN;
    let bestIndex = -1;
    for (let i = 0; i < videos.length; i++) {
        const video = videos[i];
        if (!option.softwareFilter.includes(video.software)) return;
        const thisValue = video.getStat(option.sortBy);
        if (thisValue === undefined) {
            bestValue = NaN;
            bestIndex = -1;
            break;
        }
        if (
            isNaN(bestValue)
            || thisValue > bestValue && option.sortDesc
            || thisValue < bestValue && !option.sortDesc
        ) {
            bestValue = thisValue;
            bestIndex = i;
        }
    }
    return { bestValue, bestIndex };
}
