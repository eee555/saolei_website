import type { MS_Level, MS_Mode, MS_Software } from '@/utils/ms_const';
import { isStandardLevel, MS_Softwares, MS_State } from '@/utils/ms_const';
import type { VideoAbstract } from '@/utils/videoabstract';
import { groupVideosByBBBv, groupVideosByDate } from '@/utils/videoabstract';

export type VideoSelection = { kind: 'all' } | { kind: 'date'; dateKey: string } | { kind: 'bv'; level: MS_Level; bv: number };
export interface ProfileVideoFilters {
    software: MS_Software[];
    state: string[];
    level: '' | MS_Level | 'custom';
    mode: MS_Mode[];
}
export function createProfileVideoFilters(): ProfileVideoFilters {
    return { software: [...MS_Softwares], state: Object.values(MS_State), level: '', mode: [] };
}
export function selectProfileVideos(videos: VideoAbstract[], selection: VideoSelection, useEndTime = false): VideoAbstract[] {
    if (selection.kind === 'date') return groupVideosByDate(videos, useEndTime ? 'end_time' : 'upload_time').get(selection.dateKey) ?? [];
    if (selection.kind === 'bv') return groupVideosByBBBv(videos, selection.level).get(selection.bv) ?? [];
    return videos;
}
export function filterProfileVideos(videos: VideoAbstract[], filters: ProfileVideoFilters): VideoAbstract[] {
    return videos.filter((video) => filters.software.includes(video.software)
        && filters.state.includes(video.state)
        && (!filters.level || (filters.level === 'custom' ? !isStandardLevel(video.level) : video.level === filters.level))
        && (!filters.mode.length || filters.mode.includes(video.mode)));
}
