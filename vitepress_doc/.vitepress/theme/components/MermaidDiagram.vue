<template>
    <figure class="mermaid-diagram">
        <div v-if="error" class="mermaid-diagram__error">
            {{ error }}
        </div>
        <div v-else ref="container" class="mermaid-diagram__body" />
    </figure>
</template>

<script setup lang="ts">
import { useData } from 'vitepress';
import { computed, nextTick, onMounted, ref, watch } from 'vue';

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

async function renderDiagram() {
    if (!container.value) return;

    try {
        const mermaid = (await import('mermaid')).default;
        mermaid.initialize({
            startOnLoad: false,
            securityLevel: 'strict',
            theme: isDark.value ? 'dark' : 'default',
        });

        const id = `mermaid-${Math.random().toString(36).slice(2)}`;
        const { svg } = await mermaid.render(id, source.value);
        container.value.innerHTML = svg;
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
