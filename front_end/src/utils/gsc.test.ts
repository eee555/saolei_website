import { describe, expect, it } from 'vitest';

import { GSCParticipant } from './gsc';
import { GSCDefaults } from './ms_const';

describe('GSCParticipant', () => {
    describe('constructor', () => {
        it('Default initialization', () => {
            const participant = new GSCParticipant();

            expect(participant.id).toBe(0);
            expect(participant.user__id).toBe(0);
            expect(participant.user__realname).toBe('');
            expect(participant.bt1st).toBe(GSCDefaults.bt);
            expect(participant.it1st).toBe(GSCDefaults.it);
            expect(participant.et1st).toBe(GSCDefaults.et);
        });

        it('Partial initialization', () => {
            const participant = new GSCParticipant({ id: 7, user__realname: 'Alice', bt1st: 12.34 });

            expect(participant.id).toBe(7);
            expect(participant.user__realname).toBe('Alice');
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
