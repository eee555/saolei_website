<template>
    <div class="layout-row" style="margin-bottom: 5px;">
        <span class="text-regular">
            <VideoStateIcon :state="video.state" />
            &nbsp;
            <SoftwareIcon :software="video.software" />
            &nbsp;
            {{ levelLabel }}
            &nbsp;
            {{ t(`common.mode.code${video.mode}`) }}
        </span>
    </div>
    <div class="description-layout" style="width: 32em; max-width: 100%;">
        <dl class="descriptions descriptions-bordered descriptions-small">
            <div class="description-item description-wide">
                <dt>{{ t('common.prop.upload_time') }}</dt>
                <dd>
                    {{ toISODateTimeString(video.upload_time) }}
                </dd>
            </div>

            <div v-if="video.end_time" class="description-item description-wide">
                <dt>{{ t('common.prop.end_time') }}</dt>
                <dd>
                    {{ toISODateTimeString(video.end_time) }}
                </dd>
            </div>

            <div class="description-item">
                <dt>{{ t('common.prop.time') }}</dt>
                <dd>
                    {{ video.displayStat('time') }}
                </dd>
            </div>
            <div class="description-item">
                <dt>{{ t('common.prop.bv') }}</dt>
                <dd>
                    {{ video.displayStat('bv') }}
                </dd>
            </div>
            <div class="description-item">
                <dt>{{ t('common.prop.stnb') }}</dt>
                <dd>
                    {{ video.displayStat('stnb') }}
                </dd>
            </div>

            <div class="description-item">
                <dt>{{ t('common.prop.bvs') }}</dt>
                <dd>
                    {{ video.displayStat('bvs') }}
                </dd>
            </div>
            <div class="description-item">
                <dt>{{ t('common.prop.cl_s') }}</dt>
                <dd>
                    {{ video.displayStat('cls') }}
                </dd>
            </div>
            <div class="description-item">
                <dt>{{ t('common.prop.ce_s') }}</dt>
                <dd>
                    {{ video.displayStat('ces') }}
                </dd>
            </div>

            <div class="description-item">
                <dt>{{ t('common.prop.ioe') }}</dt>
                <dd>
                    {{ video.displayStat('ioe') }}
                </dd>
            </div>
            <div class="description-item">
                <dt>{{ t('common.prop.thrp') }}</dt>
                <dd>
                    {{ video.displayStat('thrp') }}
                </dd>
            </div>
            <div class="description-item">
                <dt>{{ t('common.prop.corr') }}</dt>
                <dd>
                    {{ video.displayStat('corr') }}
                </dd>
            </div>
        </dl>
    </div>
</template>

<script setup lang="ts">
import '@/styles/descriptions.css';
import '@/styles/layout.css';
import '@/styles/text.css';
import type { PropType } from 'vue';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

import SoftwareIcon from './SoftwareIcon.vue';
import VideoStateIcon from './VideoStateIcon.vue';

import { CustomLevel } from '@/utils/customlevel';
import { toISODateTimeString } from '@/utils/datetime';
import type { VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    video: {
        type: Object as PropType<VideoAbstract>,
        required: true,
    },
});

const { t } = useI18n();

const levelLabel = computed(() => {
    if (props.video.level instanceof CustomLevel) {
        return t('common.level.c', {
            column: props.video.level.column,
            mine: props.video.level.mine,
            row: props.video.level.row,
        });
    }
    return t(`common.level.${props.video.level}`);
});
</script>
