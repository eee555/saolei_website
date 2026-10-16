// Run with node scripts/generate-invisible-character-names.mjs after upgrading the Unicode data package.
// Names uses node:zlib, so only this small, browser-safe subset is included in the frontend.
import defaultIgnorable from '@unicode/unicode-16.0.0/Binary_Property/Default_Ignorable_Code_Point/regex.mjs';
import whitespace from '@unicode/unicode-16.0.0/Binary_Property/White_Space/regex.mjs';
import control from '@unicode/unicode-16.0.0/General_Category/Control/regex.mjs';
import controlNames from '@unicode/unicode-16.0.0/Names/Control/index.mjs';
import names from '@unicode/unicode-16.0.0/Names/index.mjs';
import { writeFileSync } from 'node:fs';

const selected = {};
for (const [codePoint, name] of names) {
    const character = String.fromCodePoint(codePoint);
    if (whitespace.test(character) || defaultIgnorable.test(character) || control.test(character) || codePoint === 0x2800) {
        selected[codePoint] = name;
    }
}
for (const [codePoint, aliases] of Object.entries(controlNames)) selected[codePoint] = aliases[0];
writeFileSync(new URL('../src/components/widgets/invisibleCharacterNames.json', import.meta.url), JSON.stringify(selected, null, 2) + '\n');
