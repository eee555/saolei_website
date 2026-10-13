import '../src/setup';
import { createApp, watch } from 'vue';

import i18n from '@/i18n';
import { local } from '@/store/local';
import App from '@/views/LocalVideoAnalyzerView/App.vue';

i18n.global.locale.value = local.value.language.startsWith('zh') ? 'zh-cn' : 'en';
document.documentElement.lang = i18n.global.locale.value;
watch(() => local.value.darkmode, (dark) => {
    document.documentElement.classList.toggle('dark', dark);
}, { immediate: true });
// eslint-disable-next-line @typescript-eslint/no-unsafe-argument -- 与网站入口相同：typescript-eslint 将根 SFC 解析为 error type，SFC 类型由 vue-tsc 检查。
createApp(App).use(i18n).mount('#app');

document.body.style.margin = '0';
document.body.style.background = 'var(--ui-bg-color)';
document.getElementById('app')?.style.setProperty('height', '100vh');
