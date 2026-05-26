import path from 'path';

import { defineConfig } from 'cypress';
import vitePreprocessor from 'cypress-vite';

export default defineConfig({
    e2e: {
        baseUrl: 'http://localhost:8080',
        defaultBrowser: 'chrome',
        setupNodeEvents(on, _config) {
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
    watchForFileChanges: false,
});
