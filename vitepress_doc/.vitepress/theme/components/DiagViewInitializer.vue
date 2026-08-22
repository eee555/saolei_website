<template />

<script setup lang="ts">
import { useRoute } from 'vitepress';
import { nextTick, onMounted, onUnmounted, watch } from 'vue';
import Panzoom from '@panzoom/panzoom/dist/panzoom.es.js';
import DiagView from 'diagview';

const route = useRoute();

declare global {
    interface Window {
        Panzoom?: typeof Panzoom;
    }
}

async function initDiagView() {
    await nextTick();
    window.Panzoom = Panzoom;
    DiagView.destroy();
    DiagView.init({
        diagramSelector: '.vp-graphviz',
        layout: 'floating',
        accentColor: '#2f8fda',
        showKeyboardHelp: false,
    });
}

onMounted(() => {
    void initDiagView();
});

watch(() => route.path, () => {
    void initDiagView();
});

onUnmounted(() => {
    DiagView.destroy();
});
</script>
