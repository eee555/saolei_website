<template>
    <el-watermark v-if="local.experimental" :content="t('local.watermark')" :font="{color: 'rgba(255,0,0,0.3)', fontSize: 50}">
        <slot />
    </el-watermark>
</template>

<script setup lang="ts">
import { ElWatermark } from 'element-plus';
import { useI18n } from 'vue-i18n';

import { local } from '@/store';

/* 本地化 Localization */
const i18nMessage = {
    'zh-cn': { local: {
        watermark: '实验功能',
    } },
    'en': { local: {
        watermark: 'EXPERIMENTAL',
    } },
};

const { t } = useI18n({ messages: i18nMessage });
</script>
