<template>
    <base-tooltip :show-delay="500">
        <img style="width: 16px; height: 16px" :src="MetasweeperIcon">
        <template #content>
            <el-text>{{ t('software.metasweeper') }}</el-text>
        </template>
    </base-tooltip>
</template>

<script setup lang="ts">

import { ElText } from 'element-plus';
import { useI18n } from 'vue-i18n';

import BaseTooltip from './BaseTooltip.vue';
import { MetasweeperIcon } from '@/utils/assets';

const { t } = useI18n();

</script>
