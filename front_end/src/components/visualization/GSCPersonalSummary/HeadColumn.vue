<template>
    <div class="cell">
        <span class="text">{{ t(`common.level.short${level}`) }}</span>
    </div>
    <div v-for="i in count" class="cell">
        <span class="text">{{ i }}</span>
    </div>
    <div class="cell">
        <span class="text">{{ t('common.score.sum') }}</span>
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import { MS_Level } from '@/utils/ms_const';

const { t } = useI18n();

defineProps({
    level: {
        type: String as PropType<MS_Level | ''>,
        default: '',
    },
    count: {
        type: Number,
        default: 0,
    },
});

</script>

<style lang="less" scoped>

@import './cell.less';

</style>
