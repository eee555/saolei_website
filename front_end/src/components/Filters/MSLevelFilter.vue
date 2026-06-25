<template>
    <ElCheckboxGroup v-model="level" size="small">
        <ElCheckboxButton v-for="l in MS_Levels" :key="l" :value="l">
            {{ t(`common.level.${l}`) }}
        </ElCheckboxButton>
    </ElCheckboxGroup>
</template>

<script setup lang="ts">
import { ElCheckboxButton, ElCheckboxGroup } from 'element-plus';
import { useI18n } from 'vue-i18n';

import type { MS_Level } from '@/utils/ms_const';
import { MS_Levels } from '@/utils/ms_const';

const { t } = useI18n();

const level = defineModel({
    type: Array<MS_Level>,
    default: MS_Levels,
});
</script>

<style scoped lang="less">
::v-deep(.el-checkbox-button:first-child .el-checkbox-button__inner) {
    border-top-left-radius: 1px;
    border-bottom-left-radius: 1px;
}

::v-deep(.el-checkbox-button:last-child .el-checkbox-button__inner) {
    border-top-right-radius: 1px;
    border-bottom-right-radius: 1px;
}

::v-deep(.el-checkbox-button--small .el-checkbox-button__inner) {
    padding: 5px 8px;
    font-size: 10px;
}
</style>
