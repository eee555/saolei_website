import DefaultTheme from 'vitepress/theme';
import { inBrowser, type Theme } from 'vitepress';
import 'vitepress-plugin-graphviz/style.css';
import './style.css';
import { h } from 'vue';
import DiagViewInitializer from './components/DiagViewInitializer.vue';
import LocaleRedirect from './components/LocaleRedirect.vue';
import MermaidDiagram from './components/MermaidDiagram.vue';
import { getLocaleRedirect } from './locale-routing';

export default {
    extends: DefaultTheme,
    Layout() {
        return h(DefaultTheme.Layout, null, {
            'layout-bottom': () => h(DiagViewInitializer),
        });
    },
    enhanceApp({ app, router, siteData }) {
        app.component('DiagViewInitializer', DiagViewInitializer);
        app.component('LocaleRedirect', LocaleRedirect);
        app.component('MermaidDiagram', MermaidDiagram);
        if (inBrowser) {
            router.onBeforePageLoad = (to) => {
                const url = new URL(to, window.location.href);
                if (url.origin !== window.location.origin) return;
                const languages = navigator.languages?.length ? navigator.languages : [navigator.language];
                const target = getLocaleRedirect(url, siteData.value.base, siteData.value.themeConfig.localizedPages, languages[0] ?? 'en');
                if (target) {
                    window.location.replace(target);
                    // Finish the initial load so the server-rendered redirect page can hydrate.
                    if (router.route.component) return false;
                }
            };
        }
    },
} satisfies Theme;
