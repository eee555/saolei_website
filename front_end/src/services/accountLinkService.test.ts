import { describe, expect, it } from 'vitest';

import { getAccountLinkUpdateErrorMessageKey } from './accountLinkService';

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
