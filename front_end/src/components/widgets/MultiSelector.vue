<template>
    <ElCheckboxGroup v-model="selected">
        <ElCheckbox v-for="(option, i) in options" :key="`check-${option}`" :value="option" size="small">
            {{ _labels[i] }}
        </ElCheckbox>
    </ElCheckboxGroup>
    <ElTag v-for="(option) in selected" :key="`tag-${option}`" closable size="small" round @close="handleClose(option)">
        {{ _labels[options.indexOf(option)] }}
    </ElTag>
</template>

<script setup lang="ts">
import { ElCheckbox, ElCheckboxGroup, ElTag } from 'element-plus';
import { computed, PropType } from 'vue';

const props = defineProps({
    options: {
        type: Array as PropType<Readonly<string[]> | string[]>,
        required: true,
    },
    labels: {
        type: Array as PropType<Readonly<string[]> | string[]>,
        default: () => [],
    },
});

const selected = defineModel({
    type: Array as PropType<string[]>,
    default: () => [],
});

const _labels = computed(() => props.labels || props.options);

function handleClose(tag: string) {
    selected.value.splice(selected.value.indexOf(tag), 1);
}
</script>
