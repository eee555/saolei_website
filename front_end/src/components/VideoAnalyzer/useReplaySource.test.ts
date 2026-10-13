import { readFileSync } from 'node:fs';

import { EvfVideo } from 'ms-toollib';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { effectScope, shallowRef } from 'vue';
import type { EffectScope } from 'vue';

import type { ReplaySource } from './replayParser';
import { useReplaySource } from './useReplaySource';

const scopes: EffectScope[] = [];
function fixture(): ReplaySource {
    return { data: Uint8Array.from(readFileSync(new URL('../../../cypress/fixtures/52200.evf', import.meta.url))).buffer, filename: '52200.evf', software: 'e' };
}
function setup(input: ReplaySource) {
    const source = shallowRef<ReplaySource | null>(input);
    const scope = effectScope();
    scopes.push(scope);
    const replay = scope.run(() => useReplaySource(source));
    if (!replay) throw new Error('Replay scope did not start');
    return { scope, source, ...replay };
}
afterEach(() => {
    for (const scope of scopes.splice(0)) scope.stop();
    vi.restoreAllMocks();
});

describe('VideoAnalyzer replay sources', () => {
    it('owns independent parsers, frees replaced sources and leaves other instances and exports intact', () => {
        const input = fixture();
        const first = setup(input);
        const second = setup(input);
        const original = first.video.value;
        if (!original || !second.video.value) throw new Error('Expected loaded replays');
        expect(original).not.toBe(second.video.value);
        const free = vi.spyOn(original, 'free');
        const secondBoard = second.video.value.game_board;
        const secondIndex = second.video.value.current_event_id;
        original.current_time = 5;
        expect(second.video.value.game_board).toEqual(secondBoard);
        expect(second.video.value.current_event_id).toBe(secondIndex);
        const exported = first.createExportVideo();
        try {
            first.source.value = { ...input };
            expect(free).toHaveBeenCalledOnce();
            expect(first.video.value).not.toBe(original);
            expect(first.durationMs.value).toBe(10732);
            expect(second.durationMs.value).toBe(10732);
            exported.current_time = Infinity;
            expect(exported.bbbv_solved).toBe(52);
            first.scope.stop();
            expect(first.video.value).toBeNull();
            expect(() => first.createExportVideo()).toThrow('Replay is not loaded');
            expect(second.video.value.row).toBe(16);
        } finally {
            exported.free();
        }
    });

    it('releases a failed source and recovers when raw bytes are replaced', () => {
        const parse = vi.spyOn(EvfVideo.prototype, 'parse').mockImplementation(() => {
            throw new Error('Invalid local replay');
        });
        const free = vi.spyOn(EvfVideo.prototype, 'free');
        const replay = setup(fixture());
        expect(replay.video.value).toBeNull();
        expect(replay.errorMessage.value).toBe('Invalid local replay');
        expect(free).toHaveBeenCalledOnce();
        parse.mockRestore();
        replay.source.value = fixture();
        expect(replay.errorMessage.value).toBe('');
        expect(replay.durationMs.value).toBe(10732);
        replay.source.value = null;
        expect(replay.video.value).toBeNull();
        expect(replay.globalBoard.value).toBeNull();
        expect(free).toHaveBeenCalledTimes(2);
    });
});
