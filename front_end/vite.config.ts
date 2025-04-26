import { fileURLToPath, URL } from 'node:url';

import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import wasm from 'vite-plugin-wasm';
// import vueDevTools from 'vite-plugin-vue-devtools'
import topLevelAwait from 'vite-plugin-top-level-await';
import viteCompression from 'vite-plugin-compression';
import removeAttr from 'remove-attr';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
    process.env = { ...process.env, ...loadEnv(mode, process.cwd(), '') };
    // 真**坑爹。vite的依赖open，10.0.1修复了这个问题。但目前vite还未更新其版本
    process.env.SYSTEMROOT = process.env.SystemRoot || 'C://Windows';


    return {
        plugins: [
            vue(),
            wasm(),
            // vueDevTools(),
            topLevelAwait(),
            viteCompression({
                algorithm: 'gzip', // Or 'brotliCompress' for Brotli compression
                ext: '.gz', // Add a .gz extension to the compressed files
                threshold: 1024, // Minimum file size in bytes to compress
            }),
            process.env.NODE_ENV === 'production' ? removeAttr({
                extensions: ['vue'],
                attributes: ['data-cy'],
            }) : null,
        ],
        resolve: {
            alias: {
                '@': fileURLToPath(new URL('./src', import.meta.url)),
            },
        },
        server: {
            open: true,
            port: 8080,
            host: process.env.Host || 'localhost',
        },
        build: {
            target: ['chrome89', 'edge89', 'firefox89', 'safari15'],
        },
    // esbuild: {
    //   supported: {
    //     'top-level-await': true //browsers can handle top-level-await features
    //   },
    // },
    // build: {
    //   minify: false,
    // }
    // base: baseURL,
    };
});
