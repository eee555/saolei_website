import assert from 'node:assert/strict';
import { test } from 'node:test';

import { validateInlineHtml, writeBundledLicenses } from './offline-package.mjs';

test('allows inline scripts, textures, fonts and local SVG fragments', () => {
    const html = '<style>@font-face{src:url("data:font/woff2;base64,AA==")}div{background:url(data:image/svg+xml;base64,AA==);filter:url(#local)}</style><script type="module">const ready=true</script>';
    assert.deepEqual(validateInlineHtml(html), ['data:font/woff2;base64,AA==', 'data:image/svg+xml;base64,AA==', '#local']);
});

for (const html of ['<script src="./app.js"></script>', '<link rel="stylesheet" href="https://example.com/style.css">', '<link rel="modulepreload" href="./module.js">']) {
    test(`rejects external script/style loading: ${html}`, () => {
        assert.throws(() => validateInlineHtml(html), /external scripts or styles/);
    });
}

for (const url of ['./fonts/icons.woff2', 'https://example.com/mine.svg']) {
    test(`rejects non-inline CSS resources: ${url}`, () => {
        assert.throws(() => validateInlineHtml(`<style>.cell{background:url('${url}')}</style>`), /External CSS resources/);
    });
}

test('refuses missing dependency license texts before writing output', async () => {
    await assert.rejects(writeBundledLicenses('', []), /license list is empty/);
    await assert.rejects(writeBundledLicenses('', [{ name: 'missing-license', version: '1.0.0' }]), /missing-license@1.0.0/);
});
