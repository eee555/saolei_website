import { describe, expect, it } from 'vitest';

import { TournamentParticipant } from './tournaments';
import { WeeklyParticipant } from './weekly';

describe('WeeklyParticipant', () => {
    describe('constructor', () => {
        it('Default initialization', () => {
            const participant = new WeeklyParticipant();

            expect(participant).toBeInstanceOf(TournamentParticipant);
            expect(participant.id).toBe(0);
            expect(participant.user_id).toBeNull();
            expect(participant.classic_et).toEqual([[0, 240000], [0, 240000]]);
            expect(participant.classic_it).toEqual([
                [0, 60000],
                [0, 60000],
                [0, 60000],
                [0, 60000],
                [0, 60000],
            ]);
            expect(participant.classic_score).toBe(780000);
        });

        it('Partial initialization', () => {
            const participant = new WeeklyParticipant({
                id: 9,
                token: 'WEEKLY-TOKEN',
                user_id: 5,
                classic_et: [[1, 1234], [2, 2345]],
                classic_it: [[3, 3456]],
                classic_score: 7035,
            });

            expect(participant.id).toBe(9);
            expect(participant.token).toBe('WEEKLY-TOKEN');
            expect(participant.user_id).toBe(5);
            expect(participant.classic_e_sum).toBe(3579);
            expect(participant.classic_i_sum).toBe(3456);
            expect(participant.classic_score).toBe(7035);
        });

        it('Keeps score arrays independent between instances', () => {
            const first = new WeeklyParticipant();
            const second = new WeeklyParticipant();

            first.classic_et[0][1] = 1;

            expect(second.classic_et[0][1]).toBe(240000);
        });
    });
});
