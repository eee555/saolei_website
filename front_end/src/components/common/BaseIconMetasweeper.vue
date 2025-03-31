<template>
    <base-tooltip :show-delay="500">
        <img style="width: 16px; height: 16px" src="@/assets/img/img_meta.png">
        <template #content>
            <el-text>{{ t('common.software.metasweeper') }}</el-text>
        </template>
    </base-tooltip>
</template>

<script setup lang="ts">

import { ElText } from 'element-plus';
import BaseTooltip from './BaseTooltip.vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

</script>
