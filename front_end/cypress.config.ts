import path from 'path';
import { fileURLToPath } from 'url';

import { defineConfig } from 'cypress';
import vitePreprocessor from 'cypress-vite';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig({
    e2e: {
        baseUrl: 'http://localhost:8080',
        defaultBrowser: 'chrome',
        setupNodeEvents(on) {
            on('before:browser:launch', (browser, launchOptions) => {
                if (browser.name === 'chrome') {
                    launchOptions.args.push('--accept-lang=zh-CN');
                }
                return launchOptions;
            });
            on('file:preprocessor', vitePreprocessor({
                configFile: path.resolve(__dirname, 'vite.config.ts'),
            }));
        },
    },

    component: {
        devServer: {
            framework: 'vue',
            bundler: 'vite',
        },
    },
    chromeWebSecurity: false,
    allowCypressEnv: false,
    watchForFileChanges: false,
});
