import { fileURLToPath, URL } from 'node:url';

import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vite';
import type { Plugin } from 'vite';
import wasm from 'vite-plugin-wasm';

import { getOfflineStyles, singleFileWithLicenses } from './scripts/offline-build';

const isolatedAnalyzer: Plugin = {
    name: 'isolated-offline-analyzer',
    generateBundle() {
        const forbidden = [...this.getModuleIds()].filter((id) => (/\/src\/(?:http\.ts|store\/index\.ts|router\/index\.ts|views\/VideoAnalyzerView\/App\.vue)(?:\?|$)/u).test(id.replaceAll('\\', '/')));
        if (forbidden.length > 0) this.error(`Offline analyzer imports website modules: ${forbidden.join(', ')}`);
    },
};

export default defineConfig({
    root: fileURLToPath(new URL('./local-analyzer', import.meta.url)),
    base: './',
    publicDir: false,
    resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
    define: { 'import.meta.env.VITE_OFFLINE_ANALYZER': JSON.stringify('true') },
    css: getOfflineStyles(),
    plugins: [vue(), wasm(), isolatedAnalyzer, singleFileWithLicenses()],
    build: { target: 'esnext', outDir: '../dist-offline-analyzer', emptyOutDir: true, assetsInlineLimit: Infinity, modulePreload: false, license: { fileName: 'THIRD_PARTY_LICENSES.json' } },
});
