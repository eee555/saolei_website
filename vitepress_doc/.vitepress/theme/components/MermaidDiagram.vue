<template>
    <figure class="mermaid-diagram">
        <div v-if="error" class="mermaid-diagram__error">
            {{ error }}
        </div>
        <div
            v-else
            ref="container"
            class="mermaid-diagram__body mermaid-pan-zoom-container"
            :data-mermaid-source="source"
        />
    </figure>
</template>

<script lang="ts">
let mermaidEnhancementsInitialized = false;
</script>

<script setup lang="ts">
import { useData } from 'vitepress';
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import 'mermaid-diagram-pan-zoom/styles/mermaid-enhancements.css';

const props = defineProps({
    encodedSource: {
        type: String,
        required: true,
    },
});

const { isDark } = useData();
const container = ref<HTMLElement>();
const error = ref('');

const source = computed(() => decodeURIComponent(props.encodedSource));

async function enhanceDiagram() {
    const { init, enhance } = await import('mermaid-diagram-pan-zoom');
    if (!mermaidEnhancementsInitialized) {
        init({
            containerSelector: '.mermaid-pan-zoom-container',
            sourceAttribute: 'data-mermaid-source',
            enableCopy: true,
            enableExpand: true,
            enableInlineWheelZoom: true,
            enableWheelZoom: true,
            enableZoomControls: true,
            wheelZoomSensitivity: 0.3,
            panZoomOptions: {
                minZoom: 0.2,
                maxZoom: 8,
                zoomScaleSensitivity: 0.3,
            },
        });
        mermaidEnhancementsInitialized = true;
    }
    enhance();
}

async function renderDiagram() {
    if (!container.value) return;

    try {
        const mermaid = (await import('mermaid')).default;
        mermaid.initialize({
            startOnLoad: false,
            securityLevel: 'loose',
            theme: isDark.value ? 'dark' : 'default',
        });

        const id = `mermaid-${Math.random().toString(36).slice(2)}`;
        const { svg, bindFunctions } = await mermaid.render(id, source.value);
        container.value.innerHTML = svg;
        bindFunctions?.(container.value);
        await enhanceDiagram();
        error.value = '';
    } catch (err) {
        container.value.innerHTML = '';
        error.value = err instanceof Error ? err.message : '图示渲染失败';
    }
}

onMounted(() => {
    void nextTick(renderDiagram);
});

watch([source, isDark], () => {
    void nextTick(renderDiagram);
});
</script>
