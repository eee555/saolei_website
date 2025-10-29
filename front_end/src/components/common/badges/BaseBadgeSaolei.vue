<template>
    <img src="http://saolei.wang/favicon.ico" style="height: 16px; vertical-align: middle">
    <el-text size="small">
        {{ t('common.website.saolei') }}
    </el-text>
</template>

<script setup lang="ts">
import { ElText } from 'element-plus';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

</script>
