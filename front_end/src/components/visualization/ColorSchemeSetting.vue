<template>
    <el-row style="align-items: center">
        <el-color-picker v-model="colorScheme.colors[0]" show-alpha />
        <template v-for="(item, index) in colorScheme.thresholds" :key="index">
            &nbsp;{{ "<" }}&nbsp;
            <el-input-number v-model="colorScheme.thresholds[index]" :min="index == 0 ? -Infinity : colorScheme.thresholds[index-1]" :max="index == colorScheme.thresholds.length-1 ? Infinity : colorScheme.thresholds[index+1]" :controls="false" size="small" style="width:50px; display: inline-block" />
            &nbsp;{{ "<" }}&nbsp;
            <el-color-picker v-model="colorScheme.colors[index+1]" show-alpha />
        </template>
        <span style="flex: 1" />
        {{ "增删节点" }}
        &nbsp;
        <el-input-number v-model="operationNode" :controls="false" style="width: 40px" />
        &nbsp;
        <el-tooltip content="Add">
            <el-link :underline="false">
                <base-icon-add />
            </el-link>
        </el-tooltip>
        &nbsp;
        <el-tooltip content="Merge to left">
            <el-link :underline="false">
                <el-icon size="large">
                    <ArrowLeft />
                </el-icon>
            </el-link>
        </el-tooltip>
        &nbsp;
        <el-tooltip content="Merge to right">
            <el-link :underline="false">
                <el-icon size="large">
                    <ArrowRight />
                </el-icon>
            </el-link>
        </el-tooltip>
        &nbsp;
        <el-checkbox v-model="developerMode">
            Developer Mode
        </el-checkbox>
    </el-row>
    <el-row v-if="developerMode">
        <el-input v-model="colorSchemeString" type="textarea" :rows="countRows(colorSchemeString)" style="font-family: 'Courier New', Courier, monospace;" @change="(value: string) => {colorScheme = JSON.parse(value)}" />
    </el-row>
</template>

<script setup lang="ts">
import { ElCheckbox, ElColorPicker, ElIcon, ElInput, ElInputNumber, ElLink, ElRow, ElTooltip } from 'element-plus';
import { PropType, ref, watch } from 'vue';

import BaseIconAdd from '@/components/common/BaseIconAdd.vue';
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
