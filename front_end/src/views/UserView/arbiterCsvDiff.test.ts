import { readFileSync } from 'node:fs';

import { describe, expect, it } from 'vitest';

import { parseArbiterCsv } from './arbiterCsv';
import { compareArbiterCsv } from './arbiterCsvDiff';

import { videoToPlotPoint } from '@/components/visualization/VideoScatter/utils';
import { MS_ServerStates } from '@/utils/ms_const';
import { getStat_keys, groupVideosByBBBv, groupVideosByDate, VideoAbstract } from '@/utils/videoabstract';

const sample = readFileSync(new URL('../../../cypress/fixtures/stats_csv.csv', import.meta.url), 'utf8');
const { records } = parseArbiterCsv(sample);
const server = () => new VideoAbstract({ ...records[0].video, id: 42, end_time: '2023-10-05T21:25:57.244Z', state: 'd', ongoing_tournament: true });

describe('Arbiter CSV difference', () => {
    it('matches on second and integer milliseconds alone, across all server states', () => {
        for (const state of [...MS_ServerStates, 'e']) {
            const uploaded = server();
            Object.assign(uploaded, { state, level: 'i', bv: 10, cl: 20, software: 'e', mode: '05' });
            const result = compareArbiterCsv(records, [uploaded]);
            expect(result.localVideos).toEqual([]);
            expect(result.issues).toContainEqual({ code: 'mismatch', row: 2 });
            expect(uploaded.state).toBe(state);
        }
        expect(compareArbiterCsv(records, [server(), Object.assign(server(), { id: 43 })]).localVideos).toEqual([]);
    });

    it('generates local rows only for missing keys without changing server data', () => {
        const local = compareArbiterCsv(records, []).localVideos;
        expect(local[0]).toMatchObject({ id: 0, state: 'l', isLocal: true, timems: 35090 });
        expect(local[0].rowKey).not.toBe(server().rowKey);
        expect(local[0].displayStat('time')).toBe('35.090');
        expect(local[0].displayStat('file_size')).toBe('—');
        const other = Object.assign(server(), { timems: 35091 });
        expect(compareArbiterCsv(records, [other]).localVideos).toHaveLength(1);
        expect(other.timems).toBe(35091);
    });

    it('skips missing server dates without using upload dates as identities', () => {
        const uploaded = server();
        uploaded.end_time = undefined;
        const result = compareArbiterCsv(records, [uploaded, uploaded]);
        expect(result.localVideos).toHaveLength(1);
        expect(result.issues).toEqual([{ code: 'missingEndTime' }]);
    });

    it('keeps local keys distinct and missing stats displayable in existing groups', () => {
        const minimal = parseArbiterCsv('Day,Month,Year,Hour,Min,Sec,Time\n5,10,2023,21,25,57,35.09\n6,10,2023,21,25,57,35.09');
        const { localVideos } = compareArbiterCsv(minimal.records, []);
        expect(new Set(localVideos.map((video) => video.rowKey)).size).toBe(2);
        for (const stat of getStat_keys) expect(localVideos[0].displayStat(stat)).not.toMatch(/NaN|Infinity/);
        expect(videoToPlotPoint(localVideos[0], 'time', 'bvs')).toBeUndefined();
        const zeroTime = VideoAbstract.fromArbiterCsv({ ...records[0].video, timems: 0 });
        expect(videoToPlotPoint(zeroTime, 'time', 'bvs')).toBeUndefined();
        expect(videoToPlotPoint(zeroTime, 'timems', 'bv')).toBeDefined();
        expect(groupVideosByBBBv(localVideos, 'e').size).toBe(0);
        expect(groupVideosByDate(localVideos).size).toBe(2);
        expect(localVideos[0].upload_time).toEqual(localVideos[0].end_time);
    });
});
