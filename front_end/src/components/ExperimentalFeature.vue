<template>
    <el-watermark v-if="local.experimental" :content="t('experimentalFeature.watermark')" :font="{color: 'rgba(255,0,0,0.3)', fontSize: 50}">
        <slot />
    </el-watermark>
</template>

<script setup lang="ts">
import { local } from '@/store';
import { useI18n } from 'vue-i18n';
import { ElWatermark } from 'element-plus';

const { t } = useI18n();
</script>