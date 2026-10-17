import { readFileSync } from 'node:fs';

import type { useRafFn } from '@vueuse/core';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { computed, effectScope, isReadonly, nextTick, ref } from 'vue';
import type { EffectScope } from 'vue';

import { parseReplay } from './replayParser';
import { usePlayback } from './usePlayback';
import { useReplayPosition } from './useReplayPosition';

// Run the real VueUse scheduler with a minimal frame source in the Node test environment.
vi.mock('@vueuse/core', async (importOriginal) => {
    const original = await importOriginal<{ useRafFn: typeof useRafFn }>();
    return {
        ...original,
        useRafFn: (callback: Parameters<typeof original.useRafFn>[0], options?: Parameters<typeof original.useRafFn>[1]) => original.useRafFn(callback, {
            ...options,
            window: { requestAnimationFrame: globalThis.requestAnimationFrame, cancelAnimationFrame: globalThis.cancelAnimationFrame } as Window,
        }),
    };
});

const scopes: EffectScope[] = [];
const frames = new Map<number, FrameRequestCallback>();
let now = 0;
let nextFrameId = 0;

function setup(initialDuration = 1000) {
    const duration = ref(initialDuration);
    const scope = effectScope();
    scopes.push(scope);
    const playback = scope.run(() => usePlayback(duration));
    if (!playback) throw new Error('Playback scope did not start');
    return { duration, playback, scope };
}

function advance(ms: number) {
    now += ms;
    const pending = [...frames.values()];
    frames.clear();
    for (const callback of pending) callback(now);
}

describe('analyzer playback clock', () => {
    beforeEach(() => {
        now = 0;
        nextFrameId = 0;
        frames.clear();
        vi.spyOn(performance, 'now').mockImplementation(() => now);
        vi.stubGlobal('requestAnimationFrame', vi.fn((callback: FrameRequestCallback) => {
            const id = ++nextFrameId;
            frames.set(id, callback);
            return id;
        }));
        vi.stubGlobal('cancelAnimationFrame', vi.fn((id: number) => {
            frames.delete(id);
        }));
    });

    afterEach(() => {
        for (const scope of scopes.splice(0)) scope.stop();
        vi.restoreAllMocks();
        vi.unstubAllGlobals();
    });

    it('starts paused and exposes readonly shared state', () => {
        const { playback } = setup();
        expect(playback.currentMs.value).toBe(0);
        expect(playback.durationMs.value).toBe(1000);
        expect(playback.playbackRate.value).toBe(1);
        expect(playback.isPlaying.value).toBe(false);
        expect(playback.loopMode.value).toBe('none');
        expect(playback.canPlay.value).toBe(true);
        expect(playback.rangeStartMs.value).toBe(0);
        expect(playback.rangeEndMs.value).toBe(1000);
        expect(isReadonly(playback.currentMs)).toBe(true);
        expect(isReadonly(playback.playbackRate)).toBe(true);
        expect(isReadonly(playback.loopMode)).toBe(true);
        expect(isReadonly(playback.rangeStartMs)).toBe(true);
        expect(isReadonly(playback.rangeEndMs)).toBe(true);
        expect(frames.size).toBe(0);
    });

    it('uses elapsed time instead of a fixed increment and starts only one clock', () => {
        const { playback } = setup();
        const firstView = computed(() => playback.currentMs.value);
        const secondView = computed(() => playback.currentMs.value);
        playback.play();
        playback.play();
        expect(frames.size).toBe(1);
        advance(100);
        expect(firstView.value).toBe(100);
        expect(secondView.value).toBe(100);
        advance(233);
        expect(playback.currentMs.value).toBe(333);
    });

    it('captures time between frames on pause and excludes paused time on resume', () => {
        const { playback } = setup();
        playback.play();
        advance(100);
        now += 50;
        playback.pause();
        expect(playback.currentMs.value).toBe(150);
        expect(playback.isPlaying.value).toBe(false);
        expect(frames.size).toBe(0);
        advance(2000);
        expect(playback.currentMs.value).toBe(150);
        playback.play();
        advance(100);
        expect(playback.currentMs.value).toBe(250);
    });

    it('does not rewind when a frame timestamp precedes the playback anchor', () => {
        const { playback } = setup();
        now = 10;
        playback.play();
        const pending = [...frames.values()];
        frames.clear();
        for (const callback of pending) callback(9);
        expect(playback.currentMs.value).toBe(0);
        advance(100);
        expect(playback.currentMs.value).toBe(100);
    });

    it('rebases the clock when seeking while playing and stays paused when seeking while paused', () => {
        const { playback } = setup();
        playback.seek(200);
        expect(playback.isPlaying.value).toBe(false);
        playback.play();
        advance(100);
        now += 20;
        playback.seek(700);
        expect(playback.isPlaying.value).toBe(true);
        advance(80);
        expect(playback.currentMs.value).toBe(780);
        playback.seek(-100);
        expect(playback.currentMs.value).toBe(0);
        advance(20);
        expect(playback.currentMs.value).toBe(20);
        playback.seek(2000);
        expect(playback.currentMs.value).toBe(1000);
        expect(playback.isPlaying.value).toBe(true);
        advance(1);
        expect(playback.isPlaying.value).toBe(false);
    });

    it('changes speed without reinterpreting time elapsed at the previous rate', () => {
        const { playback } = setup(5000);
        playback.play();
        advance(100);
        now += 50;
        playback.setPlaybackRate(2);
        expect(playback.currentMs.value).toBe(150);
        advance(100);
        expect(playback.currentMs.value).toBe(350);
        playback.setPlaybackRate(0.5);
        advance(100);
        expect(playback.currentMs.value).toBe(400);
        playback.setPlaybackRate(1);
        advance(100);
        expect(playback.currentMs.value).toBe(500);
    });

    it('stops at the end after a delayed frame and restarts from the beginning on play', () => {
        const { playback } = setup();
        playback.play();
        advance(3000);
        expect(playback.currentMs.value).toBe(1000);
        expect(playback.isPlaying.value).toBe(false);
        playback.play();
        expect(playback.currentMs.value).toBe(0);
        advance(100);
        expect(playback.currentMs.value).toBe(100);
    });

    it('preserves playback state for both start and end jumps', () => {
        const { playback } = setup();
        playback.seek(1000);
        expect(playback.isPlaying.value).toBe(false);
        playback.play();
        advance(200);
        playback.seek(0);
        expect(playback.isPlaying.value).toBe(true);
        advance(100);
        expect(playback.currentMs.value).toBe(100);
        playback.seek(1000);
        expect(playback.currentMs.value).toBe(1000);
        expect(playback.isPlaying.value).toBe(true);
        advance(1);
        expect(playback.isPlaying.value).toBe(false);
    });

    it('holds the clock while dragging and continues from the released position', () => {
        const { playback } = setup();
        playback.play();
        advance(100);
        now += 20;
        playback.beginSeek();
        expect(playback.currentMs.value).toBe(120);
        expect(playback.isPlaying.value).toBe(true);
        playback.seek(750);
        advance(2000);
        expect(playback.currentMs.value).toBe(750);
        expect(playback.isPlaying.value).toBe(true);
        playback.beginSeek();
        playback.endSeek();
        advance(50);
        expect(playback.currentMs.value).toBe(800);
        now += 20;
        playback.endSeek();
        advance(30);
        expect(playback.currentMs.value).toBe(850);
    });

    it('keeps paused dragging paused and respects pause during dragging', () => {
        const { playback } = setup();
        playback.beginSeek();
        playback.seek(500);
        advance(100);
        playback.endSeek();
        expect(playback.isPlaying.value).toBe(false);
        playback.play();
        playback.beginSeek();
        playback.seek(700);
        playback.pause();
        playback.endSeek();
        advance(100);
        expect(playback.currentMs.value).toBe(700);
        expect(playback.isPlaying.value).toBe(false);
    });

    it('stops naturally after a drag to the end without rewinding on release', () => {
        const { playback } = setup();
        playback.play();
        playback.beginSeek();
        playback.seek(1000);
        advance(2000);
        expect(playback.isPlaying.value).toBe(true);
        playback.endSeek();
        expect(playback.currentMs.value).toBe(1000);
        advance(1);
        expect(playback.currentMs.value).toBe(1000);
        expect(playback.isPlaying.value).toBe(false);
    });

    it('loops the entire duration and retains elapsed time across delayed frames', () => {
        const { playback } = setup();
        playback.setLoopMode('all');
        expect(playback.isPlaying.value).toBe(false);
        playback.play();
        advance(1000);
        expect(playback.currentMs.value).toBe(0);
        expect(playback.isPlaying.value).toBe(true);
        advance(3250);
        expect(playback.currentMs.value).toBe(250);
        advance(100);
        expect(playback.currentMs.value).toBe(350);
        playback.pause();
        advance(2000);
        expect(playback.currentMs.value).toBe(350);
        playback.play();
        advance(700);
        expect(playback.currentMs.value).toBe(50);
        expect(playback.loopMode.value).toBe('all');
    });

    it('rejects loop mode changes while playing, including during a drag', () => {
        const { playback } = setup();
        playback.setLoopMode('all');
        playback.play();
        advance(800);
        playback.setLoopMode('none');
        playback.setLoopMode('range');
        expect(playback.loopMode.value).toBe('all');
        expect(playback.currentMs.value).toBe(800);
        playback.beginSeek();
        playback.setLoopMode('none');
        expect(playback.loopMode.value).toBe('all');
        playback.endSeek();
        playback.pause();
        playback.setLoopMode('none');
        expect(playback.loopMode.value).toBe('none');
        expect(playback.currentMs.value).toBe(800);
        playback.play();
        advance(200);
        expect(playback.currentMs.value).toBe(1000);
        expect(playback.isPlaying.value).toBe(false);
    });

    it('wraps a seek to the endpoint on the next frame only when looping', () => {
        const { playback } = setup();
        playback.setLoopMode('all');
        playback.seek(1000);
        expect(playback.currentMs.value).toBe(1000);
        expect(playback.isPlaying.value).toBe(false);
        playback.play();
        playback.beginSeek();
        playback.seek(1000);
        playback.endSeek();
        expect(playback.currentMs.value).toBe(1000);
        advance(100);
        expect(playback.currentMs.value).toBe(100);
        expect(playback.isPlaying.value).toBe(true);
    });

    it('handles duration changes while looping, including zero during a drag', () => {
        const { playback, duration } = setup();
        playback.setLoopMode('all');
        playback.play();
        advance(800);
        duration.value = 500;
        expect(playback.currentMs.value).toBe(300);
        expect(playback.isPlaying.value).toBe(true);
        playback.beginSeek();
        duration.value = 0;
        expect(playback.currentMs.value).toBe(0);
        expect(playback.isPlaying.value).toBe(false);
        playback.endSeek();
        playback.play();
        expect(frames.size).toBe(0);
    });

    it('immediately clamps and stops when the duration shrinks', () => {
        const { duration, playback } = setup();
        playback.play();
        advance(800);
        duration.value = 500;
        expect(playback.durationMs.value).toBe(500);
        expect(playback.currentMs.value).toBe(500);
        expect(playback.isPlaying.value).toBe(false);
        duration.value = 2000;
        expect(playback.isPlaying.value).toBe(false);
        playback.play();
        advance(100);
        expect(playback.currentMs.value).toBe(600);
    });

    it('keeps instances independent and cancels frames when their scope is disposed', () => {
        const first = setup();
        const second = setup();
        first.playback.play();
        second.playback.play();
        advance(100);
        first.scope.stop();
        expect(first.playback.isPlaying.value).toBe(false);
        advance(100);
        expect(first.playback.currentMs.value).toBe(100);
        expect(second.playback.currentMs.value).toBe(200);
        second.scope.stop();
        expect(frames.size).toBe(0);
    });

    it.each([0, -1, NaN, Infinity])('does not play with an unusable duration %s', (duration) => {
        const { playback } = setup(duration);
        playback.play();
        expect(playback.durationMs.value).toBe(0);
        expect(playback.isPlaying.value).toBe(false);
        expect(frames.size).toBe(0);
    });

    it('sets range endpoints from currentMs without seeking or starting playback', () => {
        const { playback } = setup();
        playback.seek(300);
        playback.setRangeStart();
        playback.seek(800);
        playback.setRangeEnd();
        expect(playback.rangeStartMs.value).toBe(300);
        expect(playback.rangeEndMs.value).toBe(800);
        expect(playback.currentMs.value).toBe(800);
        expect(playback.isPlaying.value).toBe(false);
        playback.seek(500);
        expect(playback.rangeStartMs.value).toBe(300);
        expect(playback.rangeEndMs.value).toBe(800);
    });

    it('resets the end to duration when a new start exceeds the chosen end', () => {
        const { playback } = setup();
        playback.seek(200);
        playback.setRangeEnd();
        playback.seek(700);
        playback.setRangeStart();
        expect(playback.rangeStartMs.value).toBe(700);
        expect(playback.rangeEndMs.value).toBe(1000);
        expect(playback.currentMs.value).toBe(700);
    });

    it('resets the start to zero when a new end precedes the chosen start', () => {
        const { playback } = setup();
        playback.seek(700);
        playback.setRangeStart();
        playback.seek(200);
        playback.setRangeEnd();
        expect(playback.rangeStartMs.value).toBe(0);
        expect(playback.rangeEndMs.value).toBe(200);
        expect(playback.currentMs.value).toBe(200);
    });

    it('keeps equal endpoints, including equal endpoints at recording boundaries', () => {
        const { playback } = setup();
        playback.seek(600);
        playback.setRangeEnd();
        playback.setRangeStart();
        expect(playback.rangeStartMs.value).toBe(600);
        expect(playback.rangeEndMs.value).toBe(600);
        playback.seek(200);
        playback.setRangeStart();
        playback.setRangeEnd();
        expect(playback.rangeStartMs.value).toBe(200);
        expect(playback.rangeEndMs.value).toBe(200);
        playback.seek(1000);
        playback.setRangeStart();
        expect(playback.rangeStartMs.value).toBe(1000);
        expect(playback.rangeEndMs.value).toBe(1000);
        playback.seek(0);
        playback.setRangeEnd();
        expect(playback.rangeStartMs.value).toBe(0);
        expect(playback.rangeEndMs.value).toBe(0);
    });

    it('marks the current frame while playing without altering the clock or stopping at the range end', () => {
        const { playback } = setup();
        playback.seek(300);
        playback.setRangeEnd();
        playback.seek(0);
        playback.play();
        advance(100);
        now += 50;
        playback.setRangeStart();
        expect(playback.rangeStartMs.value).toBe(100);
        expect(playback.currentMs.value).toBe(100);
        expect(playback.isPlaying.value).toBe(true);
        advance(250);
        expect(playback.currentMs.value).toBe(400);
        expect(playback.isPlaying.value).toBe(true);
        expect(playback.rangeEndMs.value).toBe(300);
        playback.setRangeEnd();
        expect(playback.rangeEndMs.value).toBe(400);
        advance(600);
        expect(playback.currentMs.value).toBe(1000);
        expect(playback.isPlaying.value).toBe(false);
    });

    it('restores the default range when a duration is loaded or replaced', () => {
        const { playback, duration } = setup(0);
        expect(playback.rangeEndMs.value).toBe(0);
        duration.value = 1000;
        expect(playback.rangeEndMs.value).toBe(1000);
        playback.seek(300);
        playback.setRangeStart();
        playback.seek(800);
        playback.setRangeEnd();
        duration.value = 500;
        expect(playback.rangeStartMs.value).toBe(0);
        expect(playback.rangeEndMs.value).toBe(500);
        duration.value = 0;
        expect(playback.rangeEndMs.value).toBe(0);
        duration.value = 2000;
        expect(playback.rangeStartMs.value).toBe(0);
        expect(playback.rangeEndMs.value).toBe(2000);
    });

    it('does not constrain full-recording loops to the selected range', () => {
        const { playback } = setup();
        playback.seek(300);
        playback.setRangeStart();
        playback.seek(600);
        playback.setRangeEnd();
        playback.setLoopMode('all');
        playback.seek(800);
        playback.play();
        advance(400);
        expect(playback.currentMs.value).toBe(200);
        expect(playback.loopMode.value).toBe('all');
        expect(playback.isPlaying.value).toBe(true);
        expect(playback.rangeStartMs.value).toBe(300);
        expect(playback.rangeEndMs.value).toBe(600);
    });

    it('loops a range after its end without retaining overshoot and includes both endpoints', () => {
        const { playback } = setup();
        playback.seek(200);
        playback.setRangeStart();
        playback.seek(600);
        playback.setRangeEnd();
        playback.setLoopMode('range');
        playback.seek(200);
        playback.play();
        advance(400);
        expect(playback.currentMs.value).toBe(600);
        expect(playback.isPlaying.value).toBe(true);
        advance(1);
        expect(playback.currentMs.value).toBe(200);
        advance(3000);
        expect(playback.currentMs.value).toBe(200);
        playback.setPlaybackRate(2);
        advance(100);
        expect(playback.currentMs.value).toBe(400);
        advance(101);
        expect(playback.currentMs.value).toBe(200);
        expect(playback.isPlaying.value).toBe(true);
    });

    it('immediately returns out-of-range seeks to the start while playing or dragging', () => {
        const { playback } = setup();
        playback.seek(200);
        playback.setRangeStart();
        playback.seek(600);
        playback.setRangeEnd();
        playback.setLoopMode('range');
        playback.play();
        for (const ms of [0, 1000, 601, 199]) {
            playback.seek(ms);
            expect(playback.currentMs.value).toBe(200);
            expect(playback.isPlaying.value).toBe(true);
        }
        playback.seek(600);
        expect(playback.currentMs.value).toBe(600);
        playback.beginSeek();
        playback.seek(800);
        expect(playback.currentMs.value).toBe(200);
        advance(1000);
        expect(playback.currentMs.value).toBe(200);
        playback.endSeek();
        advance(100);
        expect(playback.currentMs.value).toBe(300);
    });

    it('preserves paused out-of-range positions and returns to the start on resume', () => {
        const { playback } = setup();
        playback.seek(200);
        playback.setRangeStart();
        playback.seek(600);
        playback.setRangeEnd();
        playback.setLoopMode('range');
        for (const ms of [0, 800, 1000]) {
            playback.seek(ms);
            expect(playback.currentMs.value).toBe(ms);
            expect(playback.isPlaying.value).toBe(false);
            playback.play();
            expect(playback.currentMs.value).toBe(200);
            advance(100);
            expect(playback.currentMs.value).toBe(300);
            playback.pause();
        }
        playback.seek(700);
        playback.setRangeEnd();
        playback.seek(650);
        playback.setRangeStart();
        playback.seek(500);
        playback.play();
        expect(playback.currentMs.value).toBe(650);
    });

    it('locks range endpoints only while playing in range loop mode', () => {
        const { playback } = setup();
        playback.seek(200);
        playback.setRangeStart();
        playback.seek(600);
        playback.setRangeEnd();
        playback.setLoopMode('range');
        playback.seek(300);
        playback.play();
        playback.setRangeStart();
        playback.setRangeEnd();
        expect(playback.rangeStartMs.value).toBe(200);
        expect(playback.rangeEndMs.value).toBe(600);
        playback.pause();
        playback.setRangeStart();
        expect(playback.rangeStartMs.value).toBe(300);
        playback.setLoopMode('all');
        playback.play();
        advance(100);
        playback.setRangeEnd();
        expect(playback.rangeEndMs.value).toBe(400);
    });

    it('blocks zero-length range playback but leaves seeking, editing and other modes available', () => {
        const { playback } = setup();
        playback.seek(300);
        playback.setRangeStart();
        playback.setRangeEnd();
        playback.setLoopMode('range');
        expect(playback.canPlay.value).toBe(false);
        playback.play();
        expect(playback.isPlaying.value).toBe(false);
        expect(frames.size).toBe(0);
        playback.seek(500);
        playback.setRangeEnd();
        expect(playback.canPlay.value).toBe(true);
        playback.play();
        advance(201);
        expect(playback.currentMs.value).toBe(300);
        playback.pause();
        playback.setRangeEnd();
        for (const mode of ['none', 'all'] as const) {
            playback.setLoopMode(mode);
            expect(playback.canPlay.value).toBe(true);
            playback.play();
            advance(100);
            expect(playback.isPlaying.value).toBe(true);
            playback.pause();
        }
    });

    it('handles range loops ending at recording end and duration changes during dragging', () => {
        const { playback, duration } = setup();
        playback.seek(200);
        playback.setRangeStart();
        playback.setLoopMode('range');
        playback.seek(1000);
        playback.play();
        expect(playback.currentMs.value).toBe(1000);
        advance(1);
        expect(playback.currentMs.value).toBe(200);
        playback.beginSeek();
        duration.value = 100;
        expect(playback.rangeStartMs.value).toBe(0);
        expect(playback.rangeEndMs.value).toBe(100);
        expect(playback.currentMs.value).toBe(100);
        playback.endSeek();
        advance(1);
        expect(playback.currentMs.value).toBe(0);
        duration.value = 0;
        expect(playback.canPlay.value).toBe(false);
        expect(playback.isPlaying.value).toBe(false);
        expect(playback.currentMs.value).toBe(0);
    });

    it('restores opened and probability snapshots at the range start in a real replay', async () => {
        const bytes = Uint8Array.from(readFileSync(new URL('../../../cypress/fixtures/52200.evf', import.meta.url)));
        const video = parseReplay(bytes.buffer, '52200.evf', 'e');
        const { playback, scope } = setup(video.rtime_ms);
        try {
            const position = scope.run(() => useReplayPosition(video, playback.currentMs));
            if (position === undefined) throw new Error('Position scope did not start');
            playback.seek(5000);
            playback.setRangeStart();
            await nextTick();
            const startBoard = position.gameBoard.value;
            const startProbability = position.probabilityBoard.value;
            expect(startBoard?.flat().filter((cell) => cell >= 0 && cell <= 8)).toHaveLength(180);
            playback.seek(6000);
            playback.setRangeEnd();
            playback.setLoopMode('range');
            playback.play();
            await nextTick();
            advance(1001);
            await nextTick();
            expect(playback.currentMs.value).toBe(5000);
            expect(playback.isPlaying.value).toBe(true);
            expect(position.gameBoard.value).toEqual(startBoard);
            expect(position.probabilityBoard.value).toEqual(startProbability);
            expect(position.gameBoard.value).toEqual(video.game_board);
            expect(position.probabilityBoard.value).toEqual(video.game_board_poss);
        } finally {
            scope.stop();
            video.free();
        }
    });

    it('keeps playing after an event-index seek and restores time-based snapshots on the next frame', async () => {
        const bytes = Uint8Array.from(readFileSync(new URL('../../../cypress/fixtures/52200.evf', import.meta.url)));
        const video = parseReplay(bytes.buffer, '52200.evf', 'e');
        const { playback, scope } = setup(video.rtime_ms);
        try {
            const position = scope.run(() => useReplayPosition(video, playback.currentMs));
            if (position === undefined) throw new Error('Position scope did not start');
            playback.play();
            advance(500);
            await nextTick();
            playback.seek(0);
            position.selectKeyframe(0);
            await nextTick();
            expect(playback.isPlaying.value).toBe(true);
            expect(position.currentEventIndex.value).toBe(0);
            expect(position.gameBoard.value?.flat().every((cell) => cell === 10)).toBe(true);
            advance(1);
            await nextTick();
            expect(playback.currentMs.value).toBe(1);
            expect(playback.isPlaying.value).toBe(true);
            expect(position.currentEventIndex.value).toBe(video.current_event_id);
            expect(position.currentEventIndex.value).not.toBe(0);
            expect(position.gameBoard.value).toEqual(video.game_board);
            expect(position.probabilityBoard.value).toEqual(video.game_board_poss);
        } finally {
            scope.stop();
            video.free();
        }
    });

    it('rejects invalid time and rate inputs without changing the current playback', () => {
        const { playback } = setup();
        playback.seek(100);
        for (const rate of [0, -1, NaN, Infinity]) {
            expect(() => {
                playback.setPlaybackRate(rate);
            }).toThrow(RangeError);
        }
        for (const ms of [NaN, Infinity, -Infinity]) {
            expect(() => {
                playback.seek(ms);
            }).toThrow(RangeError);
        }
        expect(playback.currentMs.value).toBe(100);
        expect(playback.playbackRate.value).toBe(1);
    });
});
