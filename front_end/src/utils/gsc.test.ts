import { describe, expect, it } from 'vitest';

import { GSCBVMin, GSCParticipant, isGSCSupportedVideo, meetsGSCBV } from './gsc';
import { GSCDefaults, MS_Mode } from './ms_const';
import { TournamentParticipant } from './tournaments';
import { VideoAbstract } from './videoabstract';
import type { VideoAbstractData } from './videoabstract';

function replay(init: Partial<VideoAbstractData> = {}) {
    return new VideoAbstract({ level: 'e', mode: MS_Mode.Standard, timems: 40000, bv: 100, software: 'e', ...init });
}

describe('GSC score eligibility', () => {
    it.each(['b', 'i', 'e'])('accepts only STD and NF for %s', (level) => {
        for (const mode of Object.values(MS_Mode)) {
            expect(isGSCSupportedVideo(replay({ level, mode }))).toBe(mode === MS_Mode.Standard || mode === MS_Mode.NoFlag);
        }
    });

    it('rejects custom boards', () => {
        expect(isGSCSupportedVideo(replay({ level: '10x10/10' }))).toBe(false);
    });

    it.each(['b', 'i', 'e'] as const)('applies the %s BV minimum', (level) => {
        const bv = GSCBVMin[level];
        expect(meetsGSCBV(replay({ level, bv: bv - 1 }))).toBe(false);
        expect(meetsGSCBV(replay({ level, bv }))).toBe(true);
    });
});

describe('GSCParticipant', () => {
    describe('constructor', () => {
        it('Default initialization', () => {
            const participant = new GSCParticipant();

            expect(participant).toBeInstanceOf(TournamentParticipant);
            expect(participant.id).toBe(0);
            expect(participant.user_id).toBe(0);
            expect(participant.bt1st).toBe(GSCDefaults.bt);
            expect(participant.it1st).toBe(GSCDefaults.it);
            expect(participant.et1st).toBe(GSCDefaults.et);
        });

        it('Partial initialization', () => {
            const participant = new GSCParticipant({ id: 7, user_id: 1, bt1st: 12.34 });

            expect(participant.id).toBe(7);
            expect(participant.user_id).toBe(1);
            expect(participant.bt1st).toBe(12.34);
            expect(participant.it1st).toBe(GSCDefaults.it);
        });
    });

    describe('sum getters', () => {
        it('sum_tbest', () => {
            const participant = new GSCParticipant({ bt1st: 1, it1st: 2, et1st: 3 });
            expect(participant.sum_tbest).toBe(6);
        });

        it('sum_tedge', () => {
            const participant = new GSCParticipant({ bt20th: 10, it12th: 20, et5th: 30 });
            expect(participant.sum_tedge).toBe(60);
        });

        it('sum_tsum', () => {
            const participant = new GSCParticipant({ bt20sum: 100, it12sum: 200, et5sum: 300 });
            expect(participant.sum_tsum).toBe(600);
        });
    });
});
