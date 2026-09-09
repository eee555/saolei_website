import { describe, expect, it } from 'vitest';

import { MS_Mode } from './ms_const';
import { TournamentParticipant } from './tournaments';
import { VideoAbstract } from './videoabstract';
import { isWeeklyClassicScoreMode, WeeklyParticipant } from './weekly';

function video(level: 'i' | 'e', mode: MS_Mode, timems: number): VideoAbstract {
    return new VideoAbstract({
        id: timems,
        upload_time: '2026-01-01T00:00:00Z',
        level,
        mode,
        timems,
        bv: 100,
        software: 'e',
    });
}

describe('WeeklyParticipant', () => {
    describe('constructor', () => {
        it('Default initialization', () => {
            const participant = new WeeklyParticipant();

            expect(participant).toBeInstanceOf(TournamentParticipant);
            expect(participant.id).toBe(0);
            expect(participant.user_id).toBe(0);
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

    describe('classic score cache', () => {
        it('refreshes classic score fields from assigned videos without duplicating them', () => {
            const videos = [
                video('e', MS_Mode.Standard, 110000),
                video('e', MS_Mode.SpeedNG, 90000),
                video('i', MS_Mode.NoFlag, 20000),
            ];
            const participant = new WeeklyParticipant();

            participant.videos = videos;

            expect(participant.videos).toHaveLength(3);
            expect(participant.classic_et).toEqual([[110000, 110000], [0, 240000]]);
            expect(participant.classic_it).toEqual([
                [20000, 20000],
                [0, 60000],
                [0, 60000],
                [0, 60000],
                [0, 60000],
            ]);
            expect(participant.classic_score).toBe(610000);
        });

        it('appends a video and updates classic score fields using milliseconds', () => {
            const participant = new WeeklyParticipant();

            participant.addVideo(video('i', MS_Mode.Standard, 20000));

            expect(participant.videos).toHaveLength(1);
            expect(participant.classic_it[0]).toEqual([20000, 20000]);
            expect(participant.classic_i_sum).toBe(260000);
            expect(participant.classic_score).toBe(740000);
        });
    });

    describe('isWeeklyClassicScoreMode', () => {
        it('only accepts standard and no-flag modes', () => {
            expect(isWeeklyClassicScoreMode(MS_Mode.Standard)).toBe(true);
            expect(isWeeklyClassicScoreMode(MS_Mode.NoFlag)).toBe(true);
            expect(isWeeklyClassicScoreMode(MS_Mode.SpeedNG)).toBe(false);
            expect(isWeeklyClassicScoreMode(MS_Mode.Lucky)).toBe(false);
        });
    });
});
