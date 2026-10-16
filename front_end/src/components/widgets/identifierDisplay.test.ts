import { describe, expect, it } from 'vitest';

import { identifierTextParts } from './identifierDisplay';

describe('identifierTextParts', () => {
    it('marks whitespace without losing leading, trailing or repeated characters', () => {
        const text = ' a  \t\r\n\u00A0';
        const parts = identifierTextParts(text);
        expect(parts.map((part) => part.text).join('')).to.equal('␠a␠␠⇥␍↵⟦U+00A0⟧');
        expect(parts.map((part) => part.raw).join('')).to.equal(text);
        expect(parts.find((part) => part.code === 'U+00A0')?.name).to.equal('NO-BREAK SPACE');
    });

    it('reveals zero-width, bidi and control characters using Unicode names', () => {
        const parts = identifierTextParts('a\u200B\u200D\u202E\0b');
        expect(parts.filter((part) => part.code).map((part) => [part.code, part.name])).to.deep.equal([
            ['U+200B', 'ZERO WIDTH SPACE'], ['U+200D', 'ZERO WIDTH JOINER'], ['U+202E', 'RIGHT-TO-LEFT OVERRIDE'], ['U+0000', 'NULL'],
        ]);
        expect(parts.map((part) => part.text).join('')).to.equal('a⟦U+200B⟧⟦U+200D⟧⟦U+202E⟧⟦U+0000⟧b');
    });

    it('preserves visible Unicode and distinguishes literal escape markers', () => {
        const text = '汉字😀e\u0301␠⟦U+200B⟧';
        expect(identifierTextParts(text)).to.deep.equal([{ raw: text, text, code: '', name: '' }]);
    });

    it('uses full code points for supplementary variation selectors and unnamed ignorables', () => {
        const parts = identifierTextParts('字\u{E0100}\u{E0000}');
        expect(parts[1]).to.deep.equal({ raw: '\u{E0100}', text: '⟦U+E0100⟧', code: 'U+E0100', name: 'VARIATION SELECTOR-17' });
        expect(parts[2]).to.deep.equal({ raw: '\u{E0000}', text: '⟦U+E0000⟧', code: 'U+E0000', name: '' });
    });

    it('marks braille blank and handles an empty identifier', () => {
        expect(identifierTextParts('\u2800')[0]?.name).to.equal('BRAILLE PATTERN BLANK');
        expect(identifierTextParts('')).to.deep.equal([]);
    });
});
