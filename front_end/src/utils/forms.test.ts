import { describe, expect, it } from 'vitest';

import { Dict2FormData } from './forms';

describe('Dict2FormData', () => {
    it('Appends all entries', () => {
        const form = Dict2FormData({
            name: 'Ada',
            score: 42,
            active: true,
        });

        expect(form.get('name')).toBe('Ada');
        expect(form.get('score')).toBe('42');
        expect(form.get('active')).toBe('true');
    });
});
