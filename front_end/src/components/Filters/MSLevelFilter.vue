<template>
    <el-checkbox-group v-model="level" size="small">
        <el-checkbox-button v-for="l in MS_Levels" :key="l" :value="l">
            {{ t(`common.level.${l}`) }}
        </el-checkbox-button>
    </el-checkbox-group>
</template>

<script setup lang="ts">
import { MS_Level, MS_Levels } from '@/utils/ms_const';
import { useI18n } from 'vue-i18n';
import { ElCheckboxGroup, ElCheckboxButton } from 'element-plus';

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