<template>
    <el-table-column
        prop="mode" :formatter="simple_formatter((mode: string) => t(`common.mode.code${mode}`))"
        :filters="[{ text: t('common.mode.code00'), value: '00' }, { text: t('common.mode.code12'), value: '12' }, { text: t('common.mode.code05'), value: '05' }, { text: t('common.mode.code11'), value: '11' }]"
        :filter-method="defaultFilterMethod" :filter-multiple="false"
    />
</template>

<script setup lang="ts">

import { ElTableColumn } from 'element-plus';
import { useI18n } from 'vue-i18n';

import { defaultFilterMethod, simple_formatter } from '@/utils';

const { t } = useI18n();

</script>
