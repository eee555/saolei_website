<template>
    <base-tooltip :show-delay="500">
        <img style="width: 1em; height: 1em; vertical-align: -0.15em;" src="@/assets/img/img_meta.png">
        <template #content>
            <el-text>{{ t('software.metasweeper') }}</el-text>
        </template>
    </base-tooltip>
</template>

<script setup lang="ts">

import { ElText } from 'element-plus';
import { useI18n } from 'vue-i18n';

import BaseTooltip from './BaseTooltip.vue';

const { t } = useI18n();

</script>
