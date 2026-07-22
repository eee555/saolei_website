<template>
    <div style="display: flex; gap: 0.25em; align-items: center; flex-wrap: wrap; justify-content: flex-end">
        <ElColorPicker v-model="colorScheme.colors[0]" show-alpha />
        <template v-for="(item, index) in colorScheme.thresholds" :key="index">
            <span>&lt;</span>
            <InputNumber v-model="colorScheme.thresholds[index]" :min="index == 0 ? -Infinity : colorScheme.thresholds[index-1]" :max="index == colorScheme.thresholds.length-1 ? Infinity : colorScheme.thresholds[index+1]" style="field-sizing: content;" />
            <span>&lt;</span>
            <ElColorPicker v-model="colorScheme.colors[index+1]" show-alpha />
        </template>
        <span style="flex-grow: 1" />
        <div style="display: flex; flex-direction: row; gap: 0.25em; align-items: center; margin-left: 0.25em; margin-right: 0.25em">
            <span>{{ t('local.chooseNode') }}</span>
            <InputNumber v-model="operationNode" style="field-sizing: content;" />
            <div v-if="colorScheme.thresholds.includes(operationNode)" style="display: flex; margin-left: 0.25em;">
                <ElLink underline="never" :title="t('local.mergeLeft')">
                    <ElIcon size="large">
                        <ArrowLeft />
                    </ElIcon>
                </ElLink>
                <BaseIconDelete />
                <ElLink underline="never" :title="t('local.mergeRight')">
                    <ElIcon size="large">
                        <ArrowRight />
                    </ElIcon>
                </ElLink>
            </div>
            <ElLink v-else underline="never" :title="t('local.addNode')">
                <BaseIconAdd />
            </ElLink>
        </div>
        <ElCheckbox v-model="developerMode" size="small" style="margin-left: 0.5em">
            {{ t('local.developerMode') }}
        </ElCheckbox>
    </div>
    <div v-if="developerMode">
        <ElInput v-model="colorSchemeString" type="textarea" :rows="countRows(colorSchemeString)" style="font-family: 'Courier New', Courier, monospace;" @change="(value: string) => {colorScheme = JSON.parse(value)}" />
    </div>
</template>

<script setup lang="ts">
import { ElCheckbox, ElColorPicker, ElIcon, ElInput, ElLink } from 'element-plus';
import type { PropType } from 'vue';
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { BaseIconAdd, BaseIconDelete } from '@/components/common/icon';
import InputNumber from '@/components/common/InputNumber.vue';
import type { PiecewiseColorSchemeInterface } from '@/utils/colors';
import { countRows, stringifyWithLineWrap } from '@/utils/strings';

const colorScheme = defineModel({
    type: Object as PropType<PiecewiseColorSchemeInterface>,
    required: true,
});

const operationNode = ref(0);
const developerMode = ref(false);
const colorSchemeString = ref('');

watch(colorScheme.value, (value) => {
    colorSchemeString.value = stringifyWithLineWrap(value);
}, { immediate: true });

const i18nMessages = {
    'zh-cn': { local: {
        addNode: '添加',
        chooseNode: '选择节点',
        developerMode: '开发者模式',
        mergeLeft: '删除（向左合并）',
        mergeRight: '删除（向右合并）',
    } },
    en: { local: {
        addNode: 'Add',
        chooseNode: 'Choose a node',
        developerMode: 'Developer Mode',
        mergeLeft: 'Delete (merge left)',
        mergeRight: 'Delete (merge right)',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>

<style lang="less" scoped>
::v-deep(.el-input-number.is-without-controls .el-input__wrapper) {
    padding-left: 5px;
    padding-right: 5px;
}
</style>
