<template>
    <el-select v-model="value" size="small">
        <template #label="{ label }">
            <span v-if="prop.label !== ''">{{ prop.label }}: </span>
            <span>{{ label }}</span>
        </template>
        <el-option v-for="stat in options" :value="stat" :label="t('common.prop.' + stat)" />
    </el-select>
</template>

<script setup lang="ts">

import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const value = defineModel({
    type: String,
    default: '',
});

const prop = defineProps({
    label: {
        type: String,
        default: '',
    },
    options: {
        type: Array<string>,
        default: ['time', 'bv'],
    }
})

</script>