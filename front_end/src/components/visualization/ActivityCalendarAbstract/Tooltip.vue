<template>
    <el-card class="card-small">
        <span v-if="videos.length == 0" class="text">
            {{ t('activityCalendar.tooltip.noVideoOnDate', [toISODateString(date)]) }}
        </span>
        <template v-else>
            <span class="text">
                {{ t('activityCalendar.tooltip.uploadedNVideosOnDate', [toISODateString(date), videos.length]) }}
            </span>
            <br>
            <span v-for="i in count.b" :key="i" class="dot" style="background-color: #f00;" />
            <span v-for="i in count.i" :key="i" class="dot" style="background-color: #080;" />
            <span v-for="i in count.e" :key="i" class="dot" style="background-color: #00f;" />
        </template>
    </el-card>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import '@/styles/cards.css';

import { ElCard } from 'element-plus';
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { toISODateString } from '@/utils/datetime';
import { VideoAbstract } from '@/utils/videoabstract';

const { t } = useI18n();

const props = defineProps({
    date: { type: Date, required: true },
    videos: { type: Array<VideoAbstract>, default: () => [] },
});

const count = ref({ b: 0, i: 0, e: 0 });

watch(() => props.videos, () => {
    count.value.b = 0;
    count.value.i = 0;
    count.value.e = 0;
    for (const video of props.videos) {
        count.value[video.level]++;
    }
}, { immediate: true });

</script>

<style lang="less" scoped>
.dot {
    height: 12px;
    width: 12px;
    border-radius: 50%;
    display: inline-block;
}
</style>
