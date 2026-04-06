<template>
    <img :src="MetasweeperIcon" style="height: 16px; vertical-align: middle">
    <el-text size="small">
        {{ t('common.website.openms') }}
    </el-text>
</template>

<script setup lang="ts">
import { ElText } from 'element-plus';
import { useI18n } from 'vue-i18n';

import { MetasweeperIcon } from '@/utils/assets';

const { t } = useI18n();

</script>
