import { describe, expect, it } from 'vitest';

import { TournamentSeries, TournamentState } from './ms_const';
import { Tournament } from './tournaments';

describe('Tournament', () => {
    describe('constructor', () => {
        it('Default initialization', () => {
            const tournament = new Tournament({});

            expect(tournament.id).toBe(0);
            expect(tournament.name).toBe('');
            expect(tournament.description).toBeUndefined();
            expect(tournament.startDate).toBeUndefined();
            expect(tournament.endDate).toBeUndefined();
            expect(tournament.hostId).toBe(0);
            expect(tournament.hostName).toBe('');
            expect(tournament.state).toBe(TournamentState.Pending);
            expect(tournament.series).toBe(TournamentSeries.Unknown);
        });

        it('Uses camelCase fields', () => {
            const tournament = new Tournament({
                id: 1,
                name: 'Spring Cup',
                description: 'Fast games',
                startDate: '2025-01-02T03:04:05Z',
                endDate: '2025-01-03T04:05:06Z',
                hostId: 9,
                hostName: 'Host',
                state: TournamentState.Ongoing,
                series: TournamentSeries.General,
            });

            expect(tournament.id).toBe(1);
            expect(tournament.name).toBe('Spring Cup');
            expect(tournament.description).toBe('Fast games');
            expect(tournament.startDate).toEqual(new Date('2025-01-02T03:04:05Z'));
            expect(tournament.endDate).toEqual(new Date('2025-01-03T04:05:06Z'));
            expect(tournament.hostId).toBe(9);
            expect(tournament.hostName).toBe('Host');
            expect(tournament.state).toBe(TournamentState.Ongoing);
            expect(tournament.series).toBe(TournamentSeries.General);
        });

        it('Uses snake_case fallback fields', () => {
            const tournament = new Tournament({
                start_time: '2025-02-02T03:04:05Z',
                end_time: '2025-02-03T04:05:06Z',
                host_id: 11,
                host_realname: 'Fallback Host',
            });

            expect(tournament.startDate).toEqual(new Date('2025-02-02T03:04:05Z'));
            expect(tournament.endDate).toEqual(new Date('2025-02-03T04:05:06Z'));
            expect(tournament.hostId).toBe(11);
            expect(tournament.hostName).toBe('Fallback Host');
        });
    });

    describe('getLocalDescription', () => {
        it('String description', () => {
            const tournament = new Tournament({ description: 'Plain text' });
            expect(tournament.getLocalDescription('zh-CN')).toBe('Plain text');
        });

        it('Locale fallback', () => {
            const tournament = new Tournament({
                description: {
                    en: 'English',
                    zh: 'Chinese',
                },
            });

            expect(tournament.getLocalDescription('zh-CN')).toBe('Chinese');
            expect(tournament.getLocalDescription('fr')).toBe('English');
            expect(tournament.getLocalDescription('zh')).toBe('Chinese');
        });

        it('Missing description returns empty string', () => {
            const tournament = new Tournament({});
            expect(tournament.getLocalDescription('en')).toBe('');
        });
    });

    describe('getLocalName', () => {
        it('String name', () => {
            const tournament = new Tournament({ name: 'Cup' });
            expect(tournament.getLocalName('fr')).toBe('Cup');
        });

        it('Locale fallback for object name', () => {
            const tournament = new Tournament({
                name: {
                    en: 'Cup',
                    zh: '杯赛',
                },
            });

            expect(tournament.getLocalName('zh-Hans')).toBe('杯赛');
            expect(tournament.getLocalName('fr')).toBe('Cup');
        });
    });

    describe('localFallback', () => {
        it('Chinese variants fall back to zh', () => {
            expect(Tournament.localFallback('zh-CN')).toBe('zh');
        });

        it('Unknown locales fall back to en', () => {
            expect(Tournament.localFallback('fr')).toBe('en');
        });

        it('Base locales end fallback chain', () => {
            expect(Tournament.localFallback('zh')).toBeUndefined();
            expect(Tournament.localFallback('en')).toBeUndefined();
            expect(Tournament.localFallback(undefined)).toBeUndefined();
        });
    });

    describe('display time', () => {
        it('displayStartTime', () => {
            const tournament = new Tournament({ startDate: new Date(2025, 0, 5, 8, 9, 10) });
            expect(tournament.displayStartTime()).toBe('2025-01-05 08:09:10');
        });

        it('displayEndTime', () => {
            const tournament = new Tournament({ endDate: new Date(2025, 0, 5, 8, 9, 10) });
            expect(tournament.displayEndTime()).toBe('2025-01-05 08:09:10');
        });

        it('Missing dates return empty string', () => {
            const tournament = new Tournament({});
            expect(tournament.displayStartTime()).toBe('');
            expect(tournament.displayEndTime()).toBe('');
        });
    });

    describe('validation state', () => {
        it('can validate pending tournaments with a valid time range', () => {
            const tournament = new Tournament({
                state: TournamentState.Pending,
                startDate: '2025-01-01T00:00:00Z',
                endDate: '2025-01-02T00:00:00Z',
            });

            expect(tournament.canValidate).toBe(true);
        });

        it('cannot validate tournaments with invalid time ranges', () => {
            const missingDates = new Tournament({ state: TournamentState.Pending });
            const reversedDates = new Tournament({
                state: TournamentState.Pending,
                startDate: '2025-01-02T00:00:00Z',
                endDate: '2025-01-01T00:00:00Z',
            });

            expect(missingDates.canValidate).toBe(false);
            expect(reversedDates.canValidate).toBe(false);
        });

        it('cannot validate tournaments that are already active or finalized', () => {
            const states = [
                TournamentState.Awarded,
                TournamentState.Finished,
                TournamentState.Ongoing,
                TournamentState.Preparing,
            ];

            for (const state of states) {
                expect(new Tournament({
                    state,
                    startDate: '2025-01-01T00:00:00Z',
                    endDate: '2025-01-02T00:00:00Z',
                }).canValidate).toBe(false);
            }
        });

        it('can invalidate every state except awarded and cancelled', () => {
            expect(new Tournament({ state: TournamentState.Awarded }).canInvalidate).toBe(false);
            expect(new Tournament({ state: TournamentState.Cancelled }).canInvalidate).toBe(false);
            expect(new Tournament({ state: TournamentState.Pending }).canInvalidate).toBe(true);
            expect(new Tournament({ state: TournamentState.Ongoing }).canInvalidate).toBe(true);
        });
    });
});
