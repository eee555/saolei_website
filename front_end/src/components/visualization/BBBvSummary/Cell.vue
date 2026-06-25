<template>
    <span class="cell" :class="isNew ? 'cell-new' : ''">
        <template v-if="bestIndex == -1">
            &nbsp;
        </template>
        <template v-else>
            <SoftwareIcon v-if="props.showIcon === 'software'" :software="videos[bestIndex].software" />
            <VideoStateIcon v-else-if="props.showIcon === 'state'" :state="videos[bestIndex].state" />
            <ElLink underline="never" style="font-weight: inherit" @click="handleClick">
                {{ videos[bestIndex].displayStat(displayBy) }}
            </ElLink>
        </template>
    </span>
</template>

<script setup lang="ts">
import { ElLink } from 'element-plus';
import tinycolor from 'tinycolor2';
import type { PropType } from 'vue';
import { computed, ref, watch } from 'vue';

import { getBest } from './utils';

import SoftwareIcon from '@/components/widgets/SoftwareIcon.vue';
import VideoStateIcon from '@/components/widgets/VideoStateIcon.vue';
import { store } from '@/store';
import { getTextColor, PiecewiseColorScheme } from '@/utils/colors';
import { preview } from '@/utils/common/PlayerDialog';
import { fullDay, globalNow } from '@/utils/datetime';
import type { MS_Software } from '@/utils/ms_const';
import { MS_Softwares } from '@/utils/ms_const';
import type { getStat_stat, VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    videos: { type: Array<VideoAbstract>, default: [] },
    sortBy: { type: String as PropType<getStat_stat>, default: 'timems' },
    sortDesc: { type: Boolean, default: false },
    displayBy: { type: String as PropType<getStat_stat>, default: 'time' },
    colorTheme: { type: Object as PropType<PiecewiseColorScheme>, default: new PiecewiseColorScheme([], []) },
    softwareFilter: { type: Array<MS_Software>, default: () => [...MS_Softwares] },
    tooltipMode: { type: String as PropType<'fast' | 'advanced'>, default: 'fast' },
    showIcon: { type: String as PropType<'' | 'software' | 'state'>, default: '' },
    newThresh: { type: Number, default: 1 },
    newDateField: { type: String as PropType<'upload_time' | 'end_time'>, default: 'upload_time' },
});

const bestIndex = ref(-1);

function refresh() {
    const bests = getBest(props.videos, {
        sortBy: props.sortBy,
        sortDesc: props.sortDesc,
        softwareFilter: props.softwareFilter,
    });
    bestIndex.value = bests.bestIndex;
}

watch(props, refresh, { immediate: true });

const color = computed(() => {
    if (bestIndex.value === -1) return 'rgba(0,0,0,0)';
    return props.colorTheme.getColor(props.videos[bestIndex.value].getStat(props.displayBy));
});

const fontColor = computed(() => {
    const tc = tinycolor(color.value);
    return tc.getAlpha() == 0 ? getTextColor() : tc.isDark() ? 'white' : 'black';
});

const isNew = computed(() => {
    if (bestIndex.value === -1) return false;
    const time = props.videos[bestIndex.value][props.newDateField];
    if (!time) return false;
    return globalNow.value.getTime() - time.getTime() < props.newThresh * fullDay;
});

function handleClick() {
    if (props.tooltipMode === 'fast') {
        void preview(props.videos[bestIndex.value].id);
    } else {
        store.video_list = props.videos;
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

.cell-new {
    font-weight: 1000;
}

.el-link {
    --el-link-text-color: v-bind(fontColor);
}
</style>
