import { defineConfig } from 'cypress';

export default defineConfig({
    e2e: {
        baseUrl: 'http://localhost:8080',
        setupNodeEvents(_on, _config) {
            // implement node event listeners here
        },
    },

    component: {
        devServer: {
            framework: 'vue',
            bundler: 'vite',
        },
    },
    chromeWebSecurity: false,
});
