import defaultIgnorable from '@unicode/unicode-16.0.0/Binary_Property/Default_Ignorable_Code_Point/regex.mjs';
import whitespace from '@unicode/unicode-16.0.0/Binary_Property/White_Space/regex.mjs';
import control from '@unicode/unicode-16.0.0/General_Category/Control/regex.mjs';
import { ref } from 'vue';

import invisibleCharacterNames from './invisibleCharacterNames.json';

export const showInvisibleIdentifiers = ref(false);

export interface IdentifierTextPart {
    raw: string;
    text: string;
    code: string;
    name: string;
}

const names: Readonly<Record<string, string>> = invisibleCharacterNames;
const markers: Readonly<Record<string, string>> = { ' ': '␠', '\t': '⇥', '\n': '↵', '\r': '␍' };

// Unicode whitespace and default-ignorable characters are distinct sets. Controls and BRAILLE PATTERN BLANK also need markers.
// https://www.unicode.org/faq/unsup_char.html
export function identifierTextParts(text: string): IdentifierTextPart[] {
    const parts: IdentifierTextPart[] = [];
    for (const character of text) {
        if (whitespace.test(character) || defaultIgnorable.test(character) || control.test(character) || character === '\u2800') {
            const point = character.codePointAt(0);
            if (point === undefined) continue;
            const code = `U+${point.toString(16).toUpperCase().padStart(4, '0')}`;
            parts.push({ raw: character, text: markers[character] ?? `⟦${code}⟧`, code, name: names[point] ?? '' });
        } else {
            const previous = parts.at(-1);
            if (previous?.code === '') {
                previous.raw += character;
                previous.text += character;
            } else {
                parts.push({ raw: character, text: character, code: '', name: '' });
            }
        }
    }
    return parts;
}
