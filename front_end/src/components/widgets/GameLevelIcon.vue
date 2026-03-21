<template>
    <base-tooltip v-if="level == 'b'" :show-delay="500">
        <span class="text-normal">{{ t('common.level.b') }}</span>
        <template #content>
            <span class="text-small">8x8/10</span>
        </template>
    </base-tooltip>
    <base-tooltip v-else-if="level == 'i'" :show-delay="500">
        <span class="text-normal">{{ t('common.level.i') }}</span>
        <template #content>
            <span class="text-small">16x16/40</span>
        </template>
    </base-tooltip>
    <base-tooltip v-else-if="level == 'e'" :show-delay="500">
        <span class="text-normal">{{ t('common.level.e') }}</span>
        <template #content>
            <span class="text-small">30x16/99</span>
        </template>
    </base-tooltip>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseTooltip from '@/components/common/BaseTooltip.vue';
import { MS_Level } from '@/utils/ms_const';

const { t } = useI18n();

defineProps({
    level: {
        type: String as PropType<MS_Level>,
        required: true,
    },
});
</script>
