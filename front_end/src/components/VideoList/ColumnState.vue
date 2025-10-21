<template>
    <el-table-column
        prop="state" :width="32"
        :filters="[{ text: t('common.state.c'), value: 'c' }, { text: t('common.state.d'), value: 'd' }]"
        :filter-method="defaultFilterMethod"
    >
        <template #default="{row}: {row: VideoAbstract}">
            <VideoStateIcon :state="row.state" />
        </template>
    </el-table-column>
</template>

<script setup lang="ts">

import { ElTableColumn } from 'element-plus';
import { useI18n } from 'vue-i18n';

import VideoStateIcon from '@/components/widgets/VideoStateIcon.vue';
import { defaultFilterMethod } from '@/utils';
import { VideoAbstract } from '@/utils/videoabstract';

const { t } = useI18n();

</script>
