<template>
    上传于 {{ toISODateTimeString(video.upload_time) }}
    {{ t(`common.level.${video.level}`) }}{{ video.nf ? ' NF' : 'FL' }}
    {{ t('common.prop.time') }} = {{ (video.timems / 1000).toFixed(2) }}
    {{ t('common.prop.bbbv') }} = {{ video.bv }}
</template>

<script setup lang="ts">
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import { SaoleiVideo } from './utils';

import { toISODateTimeString } from '@/utils/datetime';

const { t } = useI18n();

defineProps({
    video: {
        type: Object as PropType<SaoleiVideo>,
        required: true,
    },
});
</script>
