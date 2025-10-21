<template>
    <el-checkbox-group v-model="level" size="small">
        <el-checkbox-button v-for="l in MS_Softwares" :key="l" :value="l">
            <SoftwareIcon :software="l" />
        </el-checkbox-button>
    </el-checkbox-group>
</template>

<script setup lang="ts">
import { ElCheckboxButton, ElCheckboxGroup } from 'element-plus';

import SoftwareIcon from '@/components/widgets/SoftwareIcon.vue';
import { MS_Software, MS_Softwares } from '@/utils/ms_const';

const level = defineModel({
    type: Array<MS_Software>,
    default: () => [...MS_Softwares],
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
    padding: 1px 3px;
    font-size: 10px;
}
</style>
