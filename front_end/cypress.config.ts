import { defineConfig } from 'cypress';

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
