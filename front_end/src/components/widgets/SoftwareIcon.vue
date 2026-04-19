<template>
    <tippy v-if="local.tooltip_show" :delay="[500, 0]">
        <img style="width: 16px; height: 16px" :src="iconSrc">
        <template #content>
            <span class="text">{{ t(`common.software.${software}`) }}</span>
        </template>
    </tippy>
    <img v-else style="width: 16px; height: 16px" :src="iconSrc">
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { computed, PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import { local } from '@/store';
import { ArbiterIcon, Clone07Icon, MetasweeperIcon, ViennaIconLegacy, ViennaIconNew } from '@/utils/assets';
import { MS_Software } from '@/utils/ms_const';

const { t } = useI18n();

const props = defineProps({
    software: {
        type: String as PropType<MS_Software>,
        required: true,
    },
});

const iconSrc = computed(() => {
    switch (props.software) {
        case 'a': return ArbiterIcon;
        case 'e': return MetasweeperIcon;
        case 'r': return local.value.vienna_logo_legacy ? ViennaIconLegacy : ViennaIconNew;
        case 'm': return Clone07Icon;
        default: return '';
    }
});
</script>
