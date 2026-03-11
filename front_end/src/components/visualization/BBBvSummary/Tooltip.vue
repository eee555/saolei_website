<template>
    <el-card v-if="bestIndex > -1" class="card-small">
        <video-abstract-display :video="videos[bestIndex]" />
    </el-card>
</template>

<script setup lang="ts">
import '@/styles/cards.css';
import { ElCard } from 'element-plus';
import { PropType, ref, watch } from 'vue';

import { getBest } from './utils';

import VideoAbstractDisplay from '@/components/widgets/VideoAbstractDisplay.vue';
import { MS_Software, MS_Softwares } from '@/utils/ms_const';
import { getStat_stat, VideoAbstract } from '@/utils/videoabstract';

const bestValue = ref<number>(NaN);
const bestIndex = ref(-1);

const prop = defineProps({
    videos: { type: Array<VideoAbstract>, default: [] },
    sortBy: { type: String as PropType<getStat_stat>, default: 'timems' },
    sortDesc: { type: Boolean, default: false },
    softwareFilter: { type: Array<MS_Software>, default: () => [...MS_Softwares] },
});

function refresh() {
    const bests = getBest(prop.videos, {
        sortBy: prop.sortBy,
        sortDesc: prop.sortDesc,
        softwareFilter: prop.softwareFilter,
    });
    bestValue.value = bests.bestValue;
    bestIndex.value = bests.bestIndex;
}

watch(prop, refresh, { immediate: true });

</script>
