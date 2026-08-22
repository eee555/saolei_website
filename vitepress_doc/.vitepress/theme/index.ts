import DefaultTheme from 'vitepress/theme';
import 'vitepress-plugin-graphviz/style.css';
import './style.css';
import { h } from 'vue';
import DiagViewInitializer from './components/DiagViewInitializer.vue';
import LocaleRedirect from './components/LocaleRedirect.vue';
import MermaidDiagram from './components/MermaidDiagram.vue';

export default {
    extends: DefaultTheme,
    Layout() {
        return h(DefaultTheme.Layout, null, {
            'layout-bottom': () => h(DiagViewInitializer),
        });
    },
    enhanceApp({ app }) {
        app.component('DiagViewInitializer', DiagViewInitializer);
        app.component('LocaleRedirect', LocaleRedirect);
        app.component('MermaidDiagram', MermaidDiagram);
    },
};
