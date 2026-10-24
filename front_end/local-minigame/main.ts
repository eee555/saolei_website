import '../src/styles/theme/index.css';
import '../src/styles/text.css';

import { createApp } from 'vue';
import { createI18n } from 'vue-i18n';

import App from './App.vue';

const i18n = createI18n({
    legacy: false,
    locale: navigator.language.toLowerCase().startsWith('zh') ? 'zh-cn' : 'en',
    fallbackLocale: 'en',
    messages: {},
});

// eslint-disable-next-line @typescript-eslint/no-unsafe-argument -- 与网站和 Analyzer 入口一致：根 SFC 的类型由 vue-tsc 检查。
createApp(App).use(i18n).mount('#app');
