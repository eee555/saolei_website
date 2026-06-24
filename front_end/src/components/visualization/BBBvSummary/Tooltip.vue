<template>
    <ElCard v-if="bestIndex > -1" class="card-small">
        <VideoAbstractDisplay :video="videos[bestIndex]" />
    </ElCard>
</template>

<script setup lang="ts">
import '@/styles/cards.css';
import { ElCard } from 'element-plus';
import type { PropType } from 'vue';
import { ref, watch } from 'vue';

import { getBest } from './utils';

import VideoAbstractDisplay from '@/components/widgets/VideoAbstractDisplay.vue';
import type { MS_Software } from '@/utils/ms_const';
import { MS_Softwares } from '@/utils/ms_const';
import type { getStat_stat, VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    videos: { type: Array<VideoAbstract>, default: [] },
    sortBy: { type: String as PropType<getStat_stat>, default: 'timems' },
    sortDesc: { type: Boolean, default: false },
    softwareFilter: { type: Array<MS_Software>, default: () => [...MS_Softwares] },
});
const bestValue = ref<number>(NaN);
const bestIndex = ref(-1);

function refresh() {
    const bests = getBest(props.videos, {
        sortBy: props.sortBy,
        sortDesc: props.sortDesc,
        softwareFilter: props.softwareFilter,
    });
    bestValue.value = bests.bestValue;
    bestIndex.value = bests.bestIndex;
}

watch(props, refresh, { immediate: true });
</script>
