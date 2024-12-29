<template>
    <el-checkbox-group v-model="level" size="small">
        <el-checkbox-button v-for="l in ['b', 'i', 'e']" :value="l">
            {{ t('common.level.' + l) }}
        </el-checkbox-button>
    </el-checkbox-group>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';


const { t } = useI18n();

const level = defineModel({
    type: Array<"b" | "i" | "e">,
    default: ['b', 'i', 'e'],
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