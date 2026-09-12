import { describe, expect, it } from 'vitest';

import { getAccountLinkUpdateErrorMessageKey, getMineracerAccountLinkErrorMessageKey } from './accountLinkService';

describe('getAccountLinkUpdateErrorMessageKey', () => {
    it('maps known backend account update categories to update error messages', () => {
        const cases = [
            ['cooldown', 'accountlink.updateError.cooldown'],
            ['empty', 'accountlink.updateError.empty'],
            ['indexerror', 'accountlink.updateError.indexerror'],
            ['pageempty', 'accountlink.updateError.pageempty'],
            ['requestexception', 'accountlink.updateError.requestexception'],
            ['timeout', 'accountlink.updateError.timeout'],
        ] as const;

        for (const [category, messageKey] of cases) {
            expect(getAccountLinkUpdateErrorMessageKey(category)).toBe(messageKey);
        }
    });

    it('falls back to the unknown message for missing or unexpected categories', () => {
        expect(getAccountLinkUpdateErrorMessageKey()).toBe('accountlink.updateError.unknown');
        expect(getAccountLinkUpdateErrorMessageKey('new-backend-category')).toBe('accountlink.updateError.unknown');
    });
});

describe('getMineracerAccountLinkErrorMessageKey', () => {
    it('maps known backend Mineracer categories to link error messages', () => {
        const cases = [
            ['already_linked', 'accountlink.mineracer.error.already_linked'],
            ['expired', 'accountlink.mineracer.error.expired'],
            ['identifier_conflict', 'accountlink.mineracer.error.identifier_conflict'],
            ['invalid_userid', 'accountlink.mineracer.error.invalid_userid'],
            ['not_configured', 'accountlink.mineracer.error.not_configured'],
            ['pending_start', 'accountlink.mineracer.error.pending_start'],
            ['remote_failed', 'accountlink.mineracer.error.remote_failed'],
            ['requestexception', 'accountlink.mineracer.error.requestexception'],
            ['response', 'accountlink.mineracer.error.response'],
            ['timeout', 'accountlink.mineracer.error.timeout'],
        ] as const;

        for (const [category, messageKey] of cases) {
            expect(getMineracerAccountLinkErrorMessageKey(category)).toBe(messageKey);
        }
    });

    it('falls back to the unknown Mineracer message for missing or unexpected categories', () => {
        expect(getMineracerAccountLinkErrorMessageKey()).toBe('accountlink.mineracer.error.unknown');
        expect(getMineracerAccountLinkErrorMessageKey('new-backend-category')).toBe('accountlink.mineracer.error.unknown');
    });
});
