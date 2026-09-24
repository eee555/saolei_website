import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { effectScope, nextTick, reactive } from 'vue';
import type { EffectScope, Ref } from 'vue';

import { useParticipants } from './useParticipants';

import { fetchParticipantList } from '@/services/tournamentService';
import { store } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import { globalNow } from '@/utils/datetime';
import { MS_Mode, TournamentState } from '@/utils/ms_const';
import { Tournament, TournamentParticipant } from '@/utils/tournaments';
import { VideoAbstract } from '@/utils/videoabstract';
import { WeeklyParticipant } from '@/utils/weekly';

vi.mock('@/services/tournamentService', () => ({ fetchParticipantList: vi.fn() }));
vi.mock('@/components/Notifications', () => ({ httpErrorNotification: vi.fn() }));
vi.mock('@/store', async () => {
    const { reactive: makeReactive } = await import('vue');
    return { store: makeReactive({ login_status: 0, user: { id: 99 } }) };
});
vi.mock('@/utils/datetime', async (importOriginal) => {
    const original = await importOriginal<Record<string, unknown>>();
    const { ref } = await import('vue');
    return { ...original, globalNow: ref(new Date('2026-01-01T00:00:00Z')) };
});

const scopes: EffectScope[] = [];
const clock = globalNow as Ref<Date>;
function setup() {
    const tournament = reactive(new Tournament({ id: 1, state: TournamentState.Normal, start_time: '2026-01-01T00:00:00Z', end_time: '2026-01-02T00:00:00Z' }));
    const fetchResults = vi.fn<(id: number) => Promise<WeeklyParticipant[]>>().mockResolvedValue([]);
    const scope = effectScope();
    scopes.push(scope);
    const state = scope.run(() => useParticipants(() => tournament, (item) => new WeeklyParticipant(item), fetchResults));
    if (!state) throw new Error('Participant scope did not start');
    return { tournament, fetchResults, scope, ...state };
}

describe('public tournament participants', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        clock.value = new Date('2026-01-01T00:00:00Z');
        store.login_status = LoginStatus.IsLogin;
        store.user.id = 99;
        vi.mocked(fetchParticipantList).mockResolvedValue([new TournamentParticipant({ id: 10, user_id: 99, tournament_id: 1, token: 'old' })]);
    });
    afterEach(() => {
        scopes.splice(0).forEach((scope) => {
            scope.stop();
        });
    });

    it('fetches only at phase transitions, including finished, and switches to results after awards', async () => {
        clock.value = new Date('2025-12-31T23:59:59Z');
        const state = setup();
        expect(fetchParticipantList).not.toHaveBeenCalled();
        clock.value = new Date('2026-01-01T00:00:00Z');
        await vi.waitFor(() => {
            expect(state.loading.value).toBe(false);
        });
        await nextTick();
        expect(fetchParticipantList).toHaveBeenCalledTimes(1);
        clock.value = new Date('2026-01-01T00:00:01Z');
        await nextTick();
        expect(fetchParticipantList).toHaveBeenCalledTimes(1);
        clock.value = new Date('2026-01-02T00:00:00Z');
        await vi.waitFor(() => {
            expect(fetchParticipantList).toHaveBeenCalledTimes(2);
        });
        expect(state.state.value).toBe(TournamentState.Finished);
        state.tournament.state = TournamentState.Awarded;
        await vi.waitFor(() => {
            expect(state.fetchResults).toHaveBeenCalledWith(1);
        });
    });

    it('preserves participant identity, videos and local scores when refreshing or reordering the list', async () => {
        const state = setup();
        await vi.waitFor(() => {
            expect(state.participant.value?.id).toBe(10);
        });
        const original = state.participant.value;
        if (!original) throw new Error('Participant did not load');
        original.videos = [new VideoAbstract({ id: 123, level: 'i', timems: 10000, mode: MS_Mode.Standard, bv: 80, software: 'e' })];
        const { videos } = original;
        const score = original.classic_score;
        vi.mocked(fetchParticipantList).mockResolvedValue([
            new TournamentParticipant({ id: 11, user_id: 100, tournament_id: 1 }),
            new TournamentParticipant({ id: 10, user_id: 99, tournament_id: 1, token: 'new' }),
        ]);
        await state.refresh();
        expect(state.index.value).toBe(1);
        expect(state.participant.value).toBe(original);
        expect(original.videos).toBe(videos);
        expect(original.classic_score).toBe(score);
        expect(original.token).toBe('new');
    });

    it('does not let an in-flight list response undo registration or deletion', async () => {
        const state = setup();
        await vi.waitFor(() => {
            expect(state.loading.value).toBe(false);
        });
        let resolve!: (value: TournamentParticipant[]) => void;
        vi.mocked(fetchParticipantList).mockReturnValue(new Promise((done) => {
            resolve = done;
        }));
        const pending = state.refresh();
        state.deleted(10);
        state.registered(new WeeklyParticipant({ id: 12, user_id: 99, tournament_id: 1 }));
        resolve([new TournamentParticipant({ id: 10, user_id: 99, tournament_id: 1 })]);
        await pending;
        expect(state.participants.value.map((item) => item.id)).toEqual([12]);
        expect(state.participant.value?.id).toBe(12);
    });

    it('ignores a response after its scope has been disposed', async () => {
        let resolve!: (value: TournamentParticipant[]) => void;
        vi.mocked(fetchParticipantList).mockReturnValue(new Promise((done) => {
            resolve = done;
        }));
        const state = setup();
        state.scope.stop();
        resolve([new TournamentParticipant({ id: 10, user_id: 99 })]);
        await nextTick();
        expect(state.participants.value).toEqual([]);
    });
});
