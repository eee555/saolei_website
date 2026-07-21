import DefaultTheme from 'vitepress/theme';
import './style.css';
import LocaleRedirect from './components/LocaleRedirect.vue';
import MermaidDiagram from './components/MermaidDiagram.vue';

export default {
    extends: DefaultTheme,
    enhanceApp({ app }) {
        app.component('LocaleRedirect', LocaleRedirect);
        app.component('MermaidDiagram', MermaidDiagram);
    },
};
