<template>
    <el-result icon="warning" :title="t('accountlink.unverified')" :sub-title="t('accountlink.unverifiedText')" />
</template>

<script setup lang="ts">
import { ElResult } from 'element-plus';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>
