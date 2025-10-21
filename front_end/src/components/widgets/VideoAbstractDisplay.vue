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
        </el-text>
    </el-row>
    <el-descriptions size="small" border :column="3">
        <el-descriptions-item :label="t('common.prop.upload_time')" :span="3">
            {{ toISODateTimeString(video.upload_time) }}
        </el-descriptions-item>

        <el-descriptions-item v-if="video.end_time" :label="t('common.prop.end_time')" :span="3">
            {{ toISODateTimeString(video.end_time) }}
        </el-descriptions-item>

        <el-descriptions-item :label="t('common.prop.time')">
            {{ video.displayStat('time') }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.prop.bv')">
            {{ video.displayStat('bv') }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.prop.stnb')">
            {{ video.displayStat('stnb') }}
        </el-descriptions-item>

        <el-descriptions-item :label="t('common.prop.bvs')">
            {{ video.displayStat('bvs') }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.prop.cl_s')">
            {{ video.displayStat('cls') }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.prop.ce_s')">
            {{ video.displayStat('ces') }}
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

import { ElDescriptions, ElDescriptionsItem, ElRow, ElText } from 'element-plus';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import SoftwareIcon from './SoftwareIcon.vue';
import VideoStateIcon from './VideoStateIcon.vue';

import { toISODateTimeString } from '@/utils/datetime';
import { VideoAbstract } from '@/utils/videoabstract';

const { t } = useI18n();

defineProps({
    video: {
        type: Object as PropType<VideoAbstract>,
        required: true,
    },
});

</script>
