<template>
    <el-checkbox-group v-model="checkboxGroup" size="small" style="display:inline-block">
        <el-checkbox-button v-for="item of statelist" :key="item.state" :value="item.state">
            {{ t(`common.state.${item.state}`) }}
        </el-checkbox-button>
    </el-checkbox-group>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { ElCheckboxGroup, ElCheckboxButton } from 'element-plus';

const checkboxGroup = defineModel({ type: Array<string>, required: true });

const statelist = [
    { state: 'c' },
    { state: 'd' },
    { state: 'a' },
    { state: 'b' },
];

const { t } = useI18n();

</script>
