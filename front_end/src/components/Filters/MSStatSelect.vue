<template>
    <ElSelect v-model="value" size="small" :append-to="props.appendTo" :popper-options="props.popperOptions">
        <template #label="{ label }">
            <span v-if="props.label !== ''">{{ props.label }}: </span>
            <span>{{ label }}</span>
        </template>
        <ElOption v-for="stat in options" :key="stat" :value="stat" :label="t(`common.prop.${stat}`)" />
    </ElSelect>
</template>

<script setup lang="ts">
import { ElOption, ElSelect } from 'element-plus';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

const props = defineProps({
    label: {
        type: String,
        default: '',
    },
    options: {
        type: Array<string>,
        default: ['time', 'bv'],
    },
    appendTo: {
        type: String,
        default: undefined,
    },
    popperOptions: {
        type: Object as PropType<Record<string, unknown>>,
        default: undefined,
    },
});

const { t } = useI18n();

const value = defineModel({
    type: String,
    default: '',
});
</script>
