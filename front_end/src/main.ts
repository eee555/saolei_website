import { createApp } from 'vue'
import * as ELIcons from '@element-plus/icons-vue';

import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import $axios from './http'
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
// 全局挂载axios

import 'highlight.js/styles/stackoverflow-light.css'


const app = createApp(App)

app.config.globalProperties.$axios = $axios;


for (const name in ELIcons) {
  app.component(name, (ELIcons as any)[name]);
}

app.use(ElementPlus);
app.use(store).use(router);
app.mount('#app');

const win: any = window
if (process.env.NODE_ENV === 'development') {
  if ('__VUE_DEVTOOLS_GLOBAL_HOOK__' in win) {
    win.__VUE_DEVTOOLS_GLOBAL_HOOK__.Vue = app
  }
}


declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
  }
}

// cloc-1.94.exe .\元扫雷网 -exclude-dir=node_modules
// "ms-toollib": "file:../../ms_toollib/wasm/pkg",

// git remote set-url origin https://gitee.com/ee55/saolei_website.git
// git push -f origin main

