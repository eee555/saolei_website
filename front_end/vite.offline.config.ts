import { fileURLToPath, URL } from 'node:url';

import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vite';
import type { Plugin, PluginOption, UserConfig } from 'vite';
import { viteSingleFile } from 'vite-plugin-singlefile';
import wasm from 'vite-plugin-wasm';

const isolatedAnalyzer: Plugin = {
    name: 'isolated-offline-analyzer',
    generateBundle() {
        const forbidden = [...this.getModuleIds()].filter((id) => (/\/src\/(?:http\.ts|store\/index\.ts|router\/index\.ts|views\/VideoAnalyzerView\/App\.vue)(?:\?|$)/u).test(id.replaceAll('\\', '/')));
        if (forbidden.length > 0) this.error(`Offline analyzer imports website modules: ${forbidden.join(', ')}`);
    },
};

// The legacy SVG font uses a URL fragment, which Vite deliberately leaves external.
// Chrome and Edge use WOFF2; keep the upstream font and icon classes, with one inline font source.
const offlineStyles: UserConfig['css'] = { postcss: { plugins: [{
    postcssPlugin: 'offline-primeicons-font',
    AtRule: {
        'font-face': (rule) => {
            if (rule.nodes?.some((node) => node.type === 'decl' && node.prop === 'font-family' && node.value.toLowerCase().includes('primeicons')) !== true) return;
            rule.walkDecls('src', (declaration) => {
                declaration.value = 'url("./fonts/primeicons.woff2") format("woff2")';
            });
        },
    },
}] } };

// Collect licenses before the single-file plugin removes the JavaScript chunks.
function isBundlePlugin(option: PluginOption): option is Plugin {
    return option !== null && typeof option === 'object' && 'generateBundle' in option;
}
const singleFilePlugin = viteSingleFile();
if (!isBundlePlugin(singleFilePlugin)) throw new Error('Single-file plugin object is unavailable');
const inlineBundle = singleFilePlugin.generateBundle;
if (typeof inlineBundle !== 'function') throw new Error('Single-file generateBundle hook is unavailable');
singleFilePlugin.generateBundle = { order: 'post', handler: inlineBundle };

export default defineConfig({
    root: fileURLToPath(new URL('./local-analyzer', import.meta.url)),
    base: './',
    publicDir: false,
    resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
    define: { 'import.meta.env.VITE_OFFLINE_ANALYZER': JSON.stringify('true') },
    css: offlineStyles,
    plugins: [vue(), wasm(), isolatedAnalyzer, singleFilePlugin],
    build: { target: 'esnext', outDir: '../dist-offline-analyzer', emptyOutDir: true, assetsInlineLimit: Infinity, modulePreload: false, license: { fileName: 'THIRD_PARTY_LICENSES.json' } },
});
