import { videoMatchKey } from './arbiterCsv';
import type { ArbiterCsvRecord, CsvIssue } from './arbiterCsv';

import { MS_State } from '@/utils/ms_const';
import { VideoAbstract } from '@/utils/videoabstract';

export function compareArbiterCsv(records: ArbiterCsvRecord[], videos: VideoAbstract[]): { localVideos: VideoAbstract[]; issues: CsvIssue[] } {
    const index = new Map<string, VideoAbstract>();
    const issues: CsvIssue[] = [];
    for (const video of videos) {
        if (video.state === MS_State.Local) continue;
        const key = videoMatchKey(video.end_time, video.timems);
        if (key !== undefined) index.set(key, video);
        else if (!issues.length) issues.push({ code: 'missingEndTime' });
    }
    const localVideos: VideoAbstract[] = [];
    for (const record of records) {
        const uploaded = index.get(record.key);
        if (!uploaded) {
            localVideos.push(VideoAbstract.fromArbiterCsv(record.video));
            continue;
        }
        const fields = ['bv', 'cl', 'ce', 'right_ce'] as const;
        const different = fields.some((field) => Number.isFinite(record.video[field]) && Number.isFinite(uploaded[field]) && record.video[field] !== uploaded[field]);
        if (different || (record.video.level !== 'unknown' && record.video.level !== uploaded.level) || record.video.mode !== uploaded.mode || record.video.software !== uploaded.software) issues.push({ code: 'mismatch', row: record.row });
    }
    return { localVideos, issues };
}
