import { fileURLToPath, URL } from 'node:url';

import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vite';
import type { Plugin } from 'vite';

import { getOfflineStyles, singleFileWithLicenses } from './scripts/offline-build';

const isolatedMinigame: Plugin = {
    name: 'isolated-offline-minigame',
    generateBundle() {
        const forbidden = [...this.getModuleIds()].filter((id) => (/\/src\/(?:http\.ts|store\/|router\/|bootstrap\.ts|setup\.ts)|\/ms-toollib\//u).test(id.replaceAll('\\', '/')));
        if (forbidden.length > 0) this.error(`Offline minigame imports website or replay modules: ${forbidden.join(', ')}`);
    },
};

export default defineConfig({
    root: fileURLToPath(new URL('./local-minigame', import.meta.url)),
    base: './',
    publicDir: false,
    resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
    css: getOfflineStyles(),
    plugins: [vue(), isolatedMinigame, singleFileWithLicenses()],
    build: { target: 'es2015', outDir: '../dist-offline-minigame', emptyOutDir: true, assetsInlineLimit: Infinity, modulePreload: false, license: { fileName: 'THIRD_PARTY_LICENSES.json' } },
});
