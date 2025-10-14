<template>
    <el-checkbox-group v-model="selected">
        <el-checkbox v-for="option in options" :key="option" :label="option" size="small">
            {{ option }}
        </el-checkbox>
    </el-checkbox-group>
    <el-tag v-for="option in selected" :key="option" closable size="small" round @close="handleClose">
        {{ option }}
    </el-tag>
</template>

<script setup lang="ts">

import { ElCheckboxGroup, ElCheckbox, ElTag } from 'element-plus';
import { PropType } from 'vue';

defineProps({
    options: {
        type: Array as PropType<Readonly<string[]> | string[]>,
        required: true,
    },
});

const selected = defineModel({
    type: Array as PropType<string[]>,
    default: () => [],
});

function handleClose(tag: string) {
    selected.value.splice(selected.value.indexOf(tag), 1);
}

</script>
