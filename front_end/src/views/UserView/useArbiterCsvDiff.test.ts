import { afterEach, describe, expect, it } from 'vitest';
import { effectScope, ref } from 'vue';
import type { EffectScope } from 'vue';

import { useArbiterCsvDiff } from './useArbiterCsvDiff';

import { VideoAbstract } from '@/utils/videoabstract';

const text = 'Day,Month,Year,Hour,Min,Sec,Time,mode\n5,10,2023,21,25,57,35.09,EXP';
const file = () => new File([text], 'stats.csv');
const scopes: EffectScope[] = [];
function setup() {
    const videos = ref<VideoAbstract[]>([]);
    const valid = ref(true);
    const identity = ref('42:session');
    const own = ref(true);
    const scope = effectScope();
    scopes.push(scope);
    const result = scope.run(() => useArbiterCsvDiff(videos, valid, identity, own));
    if (!result) throw new Error('CSV scope did not start');
    return { ...result, videos, valid, identity, own, scope };
}
afterEach(() => {
    scopes.splice(0).forEach((scope) => {
        scope.stop();
    });
});

describe('local CSV lifecycle', () => {
    it('clears before each import, including failures, and permits retrying the same file', async () => {
        const state = setup();
        await state.importFile(file());
        expect(state.localVideos.value).toHaveLength(1);
        const pending = state.importFile(new File(['bad'], 'bad.csv'));
        expect(state.localVideos.value).toHaveLength(0);
        await pending;
        expect(state.failure.value?.code).toBe('headers');
        expect(state.hasCsv.value).toBe(false);
        await state.importFile(file());
        await state.importFile(file());
        expect(state.localVideos.value).toHaveLength(1);
        state.clear();
        expect(state.hasCsv.value).toBe(false);
        expect(state.localVideos.value).toEqual([]);
    });

    it('rebuilds on valid server data and removes local rows after upload without altering it', async () => {
        const state = setup();
        await state.importFile(file());
        state.valid.value = false;
        expect(state.localVideos.value).toEqual([]);
        expect(state.hasCsv.value).toBe(true);
        const uploaded = new VideoAbstract({ id: 42, level: 'e', mode: '00', software: 'a', bv: 132, timems: 35090, end_time: '2023-10-05T21:25:57.244Z', state: 'd' });
        state.videos.value = [uploaded];
        state.valid.value = true;
        expect(state.localVideos.value).toHaveLength(0);
        expect(state.videos.value[0].state).toBe('d');
        state.videos.value = [];
        expect(state.localVideos.value).toHaveLength(1);
    });

    it('rejects late imports after clear, identity change, logout or disposal', async () => {
        for (const action of ['clear', 'identity', 'own', 'scope'] as const) {
            const state = setup();
            const deferred = Promise.withResolvers<string>();
            const input = file();
            Object.defineProperty(input, 'text', { value: () => deferred.promise });
            const pending = state.importFile(input);
            if (action === 'clear') state.clear();
            if (action === 'identity') state.identity.value = '43:session';
            if (action === 'own') state.own.value = false;
            if (action === 'scope') state.scope.stop();
            deferred.resolve(text);
            await pending;
            expect(state.hasCsv.value).toBe(false);
            expect(state.localVideos.value).toEqual([]);
        }
    });

    it('does not import when the full server list is unavailable or this is another profile', async () => {
        const state = setup();
        state.valid.value = false;
        await state.importFile(file());
        expect(state.hasCsv.value).toBe(false);
        state.valid.value = true;
        state.own.value = false;
        await state.importFile(file());
        expect(state.hasCsv.value).toBe(false);
    });
});
