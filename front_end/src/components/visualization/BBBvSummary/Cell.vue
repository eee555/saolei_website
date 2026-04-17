<template>
    <span class="cell">
        <template v-if="bestIndex == -1">
            &nbsp;
        </template>
        <el-link v-else underline="never" @click="handleClick">
            <software-icon v-if="prop.showIcon === 'software'" :software="videos[bestIndex].software" />
            <video-state-icon v-else-if="prop.showIcon === 'state'" :state="videos[bestIndex].state" />
            {{ videos[bestIndex].displayStat(displayBy) }}
        </el-link>
    </span>
</template>

<script setup lang="ts">
import { ElLink } from 'element-plus';
import tinycolor from 'tinycolor2';
import { computed, PropType, ref, watch } from 'vue';

import { getBest } from './utils';

import SoftwareIcon from '@/components/widgets/SoftwareIcon.vue';
import VideoStateIcon from '@/components/widgets/VideoStateIcon.vue';
import { store } from '@/store';
import { getTextColor, PiecewiseColorScheme } from '@/utils/colors';
import { preview } from '@/utils/common/PlayerDialog';
import { MS_Level, MS_Software, MS_Softwares } from '@/utils/ms_const';
import { getStat_stat, VideoAbstract } from '@/utils/videoabstract';

const bestIndex = ref(-1);

const prop = defineProps({
    level: { type: String as PropType<MS_Level>, required: true },
    bv: { type: Number, required: true },
    videos: { type: Array<VideoAbstract>, default: [] },
    sortBy: { type: String as PropType<getStat_stat>, default: 'timems' },
    sortDesc: { type: Boolean, default: false },
    displayBy: { type: String as PropType<getStat_stat>, default: 'time' },
    colorTheme: { type: Object as PropType<PiecewiseColorScheme>, default: new PiecewiseColorScheme([], []) },
    softwareFilter: { type: Array<MS_Software>, default: () => [...MS_Softwares] },
    tooltipMode: { type: String as PropType<'fast' | 'advanced'>, default: 'fast' },
    showIcon: { type: String as PropType<'' | 'software' | 'state'>, default: '' },
});

function refresh() {
    const bests = getBest(prop.videos, {
        sortBy: prop.sortBy,
        sortDesc: prop.sortDesc,
        softwareFilter: prop.softwareFilter,
    });
    bestIndex.value = bests.bestIndex;
}

watch(prop, refresh, { immediate: true });

const color = computed(() => {
    if (bestIndex.value === -1) return 'rgba(0,0,0,0)';
    return prop.colorTheme.getColor(prop.videos[bestIndex.value].getStat(prop.displayBy) as number);
});

const fontColor = computed(() => {
    const tc = tinycolor(color.value);
    return tc.getAlpha() == 0 ? getTextColor() : tc.isDark() ? 'white' : 'black';
});

function handleClick() {
    if (prop.tooltipMode === 'fast') {
        preview(prop.videos[bestIndex.value].id);
    } else {
        store.video_list = prop.videos;
        store.video_list_show = true;
    }
}

</script>

<style lang="less" scoped>

.cell {
    background-color: v-bind(color);
    outline-style: solid;
    outline-width: 1px;
    outline-color: var(--el-border-color-lighter);
    text-align: center;
    align-items: center;
    box-sizing: border-box;
}

.el-link {
    --el-link-text-color: v-bind(fontColor);
}

</style>
