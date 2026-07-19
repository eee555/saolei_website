import DefaultTheme from 'vitepress/theme';
import './style.css';
import MermaidDiagram from './components/MermaidDiagram.vue';

export default {
    extends: DefaultTheme,
    enhanceApp({ app }) {
        app.component('MermaidDiagram', MermaidDiagram);
    },
};
