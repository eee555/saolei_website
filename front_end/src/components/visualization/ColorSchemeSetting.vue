<template>
    <div style="display: flex; gap: 0.25em; align-items: center; flex-wrap: wrap; justify-content: flex-end">
        <ElColorPicker v-model="colorScheme.colors[0]" show-alpha />
        <template v-for="(item, index) in colorScheme.thresholds" :key="index">
            <span>&lt;</span>
            <ElInputNumber v-model="colorScheme.thresholds[index]" :min="index == 0 ? -Infinity : colorScheme.thresholds[index-1]" :max="index == colorScheme.thresholds.length-1 ? Infinity : colorScheme.thresholds[index+1]" :controls="false" size="small" style="width:50px; display: inline-block" />
            <span>&lt;</span>
            <ElColorPicker v-model="colorScheme.colors[index+1]" show-alpha />
        </template>
        <span style="flex-grow: 1" />
        <div>
            {{ "增删节点" }}
            &nbsp;
            <ElInputNumber v-model="operationNode" :controls="false" style="width: 40px" />
            &nbsp;
            <ElTooltip content="Add">
                <ElLink underline="never">
                    <BaseIconAdd />
                </ElLink>
            </ElTooltip>
            &nbsp;
            <ElTooltip content="Merge to left">
                <ElLink underline="never">
                    <ElIcon size="large">
                        <ArrowLeft />
                    </ElIcon>
                </ElLink>
            </ElTooltip>
            &nbsp;
            <ElTooltip content="Merge to right">
                <ElLink underline="never">
                    <ElIcon size="large">
                        <ArrowRight />
                    </ElIcon>
                </ElLink>
            </ElTooltip>
            &nbsp;
            <ElCheckbox v-model="developerMode">
                Developer Mode
            </ElCheckbox>
        </div>
    </div>
    <div v-if="developerMode">
        <ElInput v-model="colorSchemeString" type="textarea" :rows="countRows(colorSchemeString)" style="font-family: 'Courier New', Courier, monospace;" @change="(value: string) => {colorScheme = JSON.parse(value)}" />
    </div>
</template>

<script setup lang="ts">
import { ElCheckbox, ElColorPicker, ElIcon, ElInput, ElInputNumber, ElLink, ElTooltip } from 'element-plus';
import { PropType, ref, watch } from 'vue';

import { BaseIconAdd } from '@/components/common/icon';
import { countRows, stringifyWithLineWrap } from '@/utils/strings';

interface ColorScheme {
    colors: Array<string>;
    thresholds: Array<number>;
}

const colorScheme = defineModel({
    type: Object as PropType<ColorScheme>,
    required: true,
});

const operationNode = ref(0);
const developerMode = ref(false);
const colorSchemeString = ref('');

watch(colorScheme.value, (value) => {
    colorSchemeString.value = stringifyWithLineWrap(value);
}, { immediate: true });
</script>

<style lang="less" scoped>
::v-deep(.el-input-number.is-without-controls .el-input__wrapper) {
    padding-left: 5px;
    padding-right: 5px;
}
</style>
