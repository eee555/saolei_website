<template>
    <el-row style="margin-bottom: 5px;">
        <el-text>
            <VideoStateIcon :state="video.state" />
            &nbsp;
            <SoftwareIcon :software="video.software" />
            &nbsp;
            {{ t(`common.level.${video.level}`) }}
            &nbsp;
            {{ t(`common.mode.code${video.mode}`) }}
            &nbsp;
            {{ toISODateTimeString(video.upload_time) }}
        </el-text>
    </el-row>
    <el-descriptions size="small" border :column="2">
        <el-descriptions-item :label="t('common.prop.time')">
            {{ video.displayStat('time') }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.prop.bv')">
            {{ video.displayStat('bv') }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.prop.bvs')">
            {{ video.displayStat('bvs') }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.prop.ioe')">
            {{ video.displayStat('ioe') }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.prop.thrp')">
            {{ video.displayStat('thrp') }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.prop.corr')">
            {{ video.displayStat('corr') }}
        </el-descriptions-item>
    </el-descriptions>
</template>

<script setup lang="ts">

import { PropType } from 'vue';
import { VideoAbstract } from '@/utils/videoabstract';
import { toISODateTimeString } from '@/utils/datetime';
import { ElDescriptions, ElDescriptionsItem, ElRow, ElText } from 'element-plus';
import VideoStateIcon from './VideoStateIcon.vue';
import SoftwareIcon from './SoftwareIcon.vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

defineProps({
    video: {
        type: Object as PropType<VideoAbstract>,
        required: true,
    },
});

</script>
