<template>
    <div class="custom-counter-json-editor">
        <ElInput
            v-model="configString"
            class="custom-counter-json-editor__input"
            type="textarea"
            @input="clearConfigError"
            @change="applyConfigString"
        />
        <div v-if="configErrorMessage !== ''" class="custom-counter-json-editor__error">
            {{ configErrorMessage }}
        </div>
    </div>
</template>

<script setup lang="ts">
import { ElInput } from 'element-plus';
import type { PropType } from 'vue';
import { ref, watch } from 'vue';

import { cloneCustomCounterConfig, isCustomCounterConfig } from './types';
import type { CustomCounterConfig } from './types';

import { stringifyWithLineWrap } from '@/utils/strings';

const config = defineModel({
    type: Array as PropType<CustomCounterConfig>,
    required: true,
});

const configString = ref('');
const configErrorMessage = ref('');

watch(config, (value) => {
    configString.value = stringifyWithLineWrap(value);
    configErrorMessage.value = '';
}, { deep: true, immediate: true });

function applyConfigString(value: string) {
    try {
        const parsed = JSON.parse(value) as unknown;
        if (!isCustomCounterConfig(parsed)) {
            configErrorMessage.value = '配置必须是形如 [["label", "expression"]] 的二维字符串数组。';
            return;
        }
        config.value = cloneCustomCounterConfig(parsed);
        configErrorMessage.value = '';
    } catch (error) {
        configErrorMessage.value = `JSON 解析失败：${formatConfigError(error)}`;
    }
}

function clearConfigError() {
    configErrorMessage.value = '';
}

function formatConfigError(error: unknown) {
    if (error instanceof Error && error.message !== '') return error.message;
    return String(error);
}
</script>

<style scoped>
.custom-counter-json-editor {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
    min-height: 0;
}

.custom-counter-json-editor__input {
    flex: 1 1 auto;
    width: 100%;
    min-height: 0;
    font-family: "Courier New", Courier, monospace;
}

:deep(.custom-counter-json-editor__input .el-textarea__inner) {
    height: 100%;
    min-height: 0 !important;
    overflow: auto;
    resize: none;
}

.custom-counter-json-editor__error {
    flex: 0 0 auto;
    margin-top: 6px;
    color: var(--el-color-danger);
    font-size: 12px;
    line-height: 1.35;
    overflow-wrap: anywhere;
}
</style>
