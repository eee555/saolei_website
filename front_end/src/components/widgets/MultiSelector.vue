<template>
    <el-checkbox-group v-model="selected">
        <el-checkbox v-for="i in options.length" :key="options[i]" size="small">
            {{ _labels[i] }}
        </el-checkbox>
    </el-checkbox-group>
    <el-tag v-for="i in options.length" :key="options[i]" closable size="small" round @close="handleClose">
        {{ _labels[i] }}
    </el-tag>
</template>

<script setup lang="ts">

import { ElCheckboxGroup, ElCheckbox, ElTag } from 'element-plus';
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
