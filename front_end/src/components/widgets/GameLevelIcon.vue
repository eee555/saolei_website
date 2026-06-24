<template>
    <span class="text" :title="titles[level]">{{ t(`common.level.${level}`) }}</span>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import type { MS_Level } from '@/utils/ms_const';

defineProps({
    level: {
        type: String as PropType<MS_Level>,
        required: true,
    },
});

const titles = {
    b: '8x8/10',
    i: '16x16/40',
    e: '30x16/99',
};

const { t } = useI18n();
</script>
