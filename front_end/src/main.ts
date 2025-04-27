import './setup.js';
import { createApp } from 'vue';
import * as ELIcons from '@element-plus/icons-vue';

import App from './App.vue';
import router from './router';
import i18n from '@/i18n';
import $axios from './http';
import { AxiosInstance } from 'axios';
// 全局挂载axios

import 'highlight.js/styles/stackoverflow-light.css';
import { pinia } from './store/create';


const app = createApp(App);

app.config.globalProperties.$axios = $axios;


for (const name in ELIcons) {
    app.component(name, (ELIcons as any)[name]);
}

app.use(pinia).use(router).use(i18n);
app.mount('#app');

const win: any = window;
if (import.meta.env.NODE_ENV === 'development') {
    if ('__VUE_DEVTOOLS_GLOBAL_HOOK__' in win) {
        win.__VUE_DEVTOOLS_GLOBAL_HOOK__.Vue = app;
    }
}


declare module '@vue/runtime-core' {
    interface ComponentCustomProperties {
        $axios: AxiosInstance;
    }
}

// cloc-1.94.exe .\开源扫雷网 -exclude-dir=node_modules
// "ms-toollib": "file:../../ms_toollib/wasm/pkg",

// git remote set-url origin https://gitee.com/ee55/saolei_website.git
// git push -f origin main

