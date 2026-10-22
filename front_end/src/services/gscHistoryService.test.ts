import { AxiosHeaders } from 'axios';
import { afterEach, describe, expect, it } from 'vitest';

import { bindGSCHistoryIdentifier, fetchGSCHistory, importGSCHistoryScores, prepareGSCHistory, uploadGSCHistoryVideo } from './gscHistoryService';

import { gscScoreFields } from '@/components/GSCAdmin/history';
import type { HistoryScores } from '@/components/GSCAdmin/history';
import $axios from '@/http';

describe('GSC historical import transport', () => {
    const originalAdapter = $axios.defaults.adapter;
    afterEach(() => {
        $axios.defaults.adapter = originalAdapter;
    });

    it('combines existing tournament info and result APIs for the management list', async () => {
        const requests: { url: string | undefined; params: unknown }[] = [];
        const endTime = '2020-01-01T00:00:00Z';
        $axios.defaults.adapter = (config) => {
            requests.push({ url: config.url, params: config.params });
            const data = config.url === '/api/tournament/gsc/admin-info'
                ? { id: 42, end_time: endTime }
                : [{ id: 7, user_id: 0, manual_scores: true, has_videos: false, arbiter_identifier: 'Anonymous', ...Object.fromEntries(gscScoreFields.map((field) => [field, 1000])) }];
            return Promise.resolve({ data, status: 200, statusText: 'OK', headers: new AxiosHeaders(), config });
        };
        const result = await fetchGSCHistory(19);
        expect(requests).toEqual([
            { url: '/api/tournament/gsc/admin-info', params: { order: 19 } },
            { url: '/api/tournament/gsc/results', params: { tournament_id: 42 } },
        ]);
        expect(result.tournamentId).toBe(42);
        expect(result.endTime).toEqual(new Date(endTime));
        expect(result.participants[0]).toMatchObject({ id: 7, user_id: 0, tournament_id: 42, manual_scores: true, has_videos: false, arbiter_identifier__identifier: 'Anonymous', sum_tsum: 3000 });
    });

    it('does not load results or create a fallback date when tournament end time is missing', async () => {
        const requests: string[] = [];
        $axios.defaults.adapter = (config) => {
            requests.push(config.url ?? '');
            return Promise.resolve({ data: { id: 42, end_time: null }, status: 200, statusText: 'OK', headers: new AxiosHeaders(), config });
        };
        await expect(fetchGSCHistory(19)).rejects.toThrow('Tournament end time is not set.');
        expect(requests).toEqual(['/api/tournament/gsc/admin-info']);
    });

    it('sends JSON rather than inheriting the site-wide URL-encoded default', async () => {
        const bodies: unknown[] = [];
        $axios.defaults.adapter = (config) => {
            expect(config.headers.getContentType()).toBe('application/json');
            bodies.push(JSON.parse(String(config.data)));
            const data = config.url?.endsWith('/prepare') === true ? { id: 7 } : config.url?.endsWith('/identifier') === true ? { identifier: ' Player ', bound: true } : 1;
            return Promise.resolve({ data, status: 200, statusText: 'OK', headers: new AxiosHeaders(), config });
        };
        const scores = Object.fromEntries(gscScoreFields.map((field) => [field, 1000])) as HistoryScores;
        await expect(prepareGSCHistory(19, 101)).resolves.toEqual({ id: 7 });
        await expect(bindGSCHistoryIdentifier(7, ' Player ')).resolves.toEqual({ identifier: ' Player ', bound: true });
        await importGSCHistoryScores('users', 19, [{ ...scores, user_id: 101 }]);
        expect(bodies).toEqual([{ order: 19, user_id: 101 }, { identifier: ' Player ' }, { order: 19, rows: [{ ...scores, user_id: 101 }] }]);
    });

    it('sends a timezone-qualified per-file time without replacing it with tournament end', async () => {
        const uploadTime = new Date('2019-12-31T23:59:18.979Z');
        $axios.defaults.adapter = (config) => {
            expect(config.url).toBe('/api/tournament/gsc/history/participants/7/videos');
            const body = config.data as FormData;
            expect(body.get('upload_time')).toBe(uploadTime.toISOString());
            expect((body.get('file') as File).name).toBe('replay.evf');
            return Promise.resolve({ data: { id: 8 }, status: 200, statusText: 'OK', headers: new AxiosHeaders(), config });
        };
        await expect(uploadGSCHistoryVideo(7, new File(['replay'], 'replay.evf'), uploadTime)).resolves.toEqual({ id: 8 });
    });
});
