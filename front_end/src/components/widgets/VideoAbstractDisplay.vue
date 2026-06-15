<template>
    <ElRow style="margin-bottom: 5px;">
        <span class="text">
            <VideoStateIcon :state="video.state" />
            &nbsp;
            <SoftwareIcon :software="video.software" />
            &nbsp;
            {{ t(`common.level.${video.level}`) }}
            &nbsp;
            {{ t(`common.mode.code${video.mode}`) }}
        </span>
    </ElRow>
    <ElDescriptions size="small" border :column="3">
        <ElDescriptionsItem :label="t('common.prop.upload_time')" :span="3">
            {{ toISODateTimeString(video.upload_time) }}
        </ElDescriptionsItem>

        <ElDescriptionsItem v-if="video.end_time" :label="t('common.prop.end_time')" :span="3">
            {{ toISODateTimeString(video.end_time) }}
        </ElDescriptionsItem>

        <ElDescriptionsItem :label="t('common.prop.time')">
            {{ video.displayStat('time') }}
        </ElDescriptionsItem>
        <ElDescriptionsItem :label="t('common.prop.bv')">
            {{ video.displayStat('bv') }}
        </ElDescriptionsItem>
        <ElDescriptionsItem :label="t('common.prop.stnb')">
            {{ video.displayStat('stnb') }}
        </ElDescriptionsItem>

        <ElDescriptionsItem :label="t('common.prop.bvs')">
            {{ video.displayStat('bvs') }}
        </ElDescriptionsItem>
        <ElDescriptionsItem :label="t('common.prop.cl_s')">
            {{ video.displayStat('cls') }}
        </ElDescriptionsItem>
        <ElDescriptionsItem :label="t('common.prop.ce_s')">
            {{ video.displayStat('ces') }}
        </ElDescriptionsItem>

        <ElDescriptionsItem :label="t('common.prop.ioe')">
            {{ video.displayStat('ioe') }}
        </ElDescriptionsItem>
        <ElDescriptionsItem :label="t('common.prop.thrp')">
            {{ video.displayStat('thrp') }}
        </ElDescriptionsItem>
        <ElDescriptionsItem :label="t('common.prop.corr')">
            {{ video.displayStat('corr') }}
        </ElDescriptionsItem>
    </ElDescriptions>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import { ElDescriptions, ElDescriptionsItem, ElRow } from 'element-plus';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import SoftwareIcon from './SoftwareIcon.vue';
import VideoStateIcon from './VideoStateIcon.vue';

import { toISODateTimeString } from '@/utils/datetime';
import { VideoAbstract } from '@/utils/videoabstract';

defineProps({
    video: {
        type: Object as PropType<VideoAbstract>,
        required: true,
    },
});

const { t } = useI18n();
</script>
