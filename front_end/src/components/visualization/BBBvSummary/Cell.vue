<template>
    <span class="cell" :class="{ 'cell-new': isNew, 'cell-selected': selectable && selected }" :style="cellStyle">
        <BaseTextButton v-if="selectable && videos.length > 0" class="cell-select video-cell-action" data-cy="video-cell-action" :aria-label="selectionLabel" :aria-pressed="selected" @click="emit('select')">
            <template v-if="bestIndex !== -1">
                <SoftwareIcon v-if="props.showIcon === 'software'" :software="videos[bestIndex].software" />
                <VideoStateIcon v-else-if="props.showIcon === 'state'" :state="videos[bestIndex].state" />
                {{ videos[bestIndex].displayStat(displayBy) }}
            </template>
            <template v-else>--</template>
        </BaseTextButton>
        <template v-else-if="bestIndex == -1">
            &nbsp;
        </template>
        <template v-else>
            <SoftwareIcon v-if="props.showIcon === 'software'" :software="videos[bestIndex].software" />
            <VideoStateIcon v-else-if="props.showIcon === 'state'" :state="videos[bestIndex].state" />
            <span v-if="videos[bestIndex].isLocal">{{ videos[bestIndex].displayStat(displayBy) }}</span>
            <VideoPreviewLink v-else :id="videos[bestIndex].id" :video="videos[bestIndex]" :show-software="false" :show-tooltip="false" class="video-cell-action" data-cy="video-cell-action">
                {{ videos[bestIndex].displayStat(displayBy) }}
            </VideoPreviewLink>
        </template>
    </span>
</template>

<script setup lang="ts">
import type { PropType } from 'vue';
import { computed, ref, watch } from 'vue';

import { getBest } from './utils';

import BaseTextButton from '@/components/common/BaseTextButton.vue';
import VideoPreviewLink from '@/components/VideoPreviewLink.vue';
import SoftwareIcon from '@/components/widgets/SoftwareIcon.vue';
import VideoStateIcon from '@/components/widgets/VideoStateIcon.vue';
import { PiecewiseColorScheme } from '@/utils/colors';
import { fullDay, globalNow } from '@/utils/datetime';
import type { MS_Software } from '@/utils/ms_const';
import { MS_Softwares } from '@/utils/ms_const';
import type { getStat_stat, VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    selectable: { type: Boolean, default: false },
    selected: { type: Boolean, default: false },
    selectionLabel: { type: String, default: '' },
    videos: { type: Array<VideoAbstract>, default: [] },
    sortBy: { type: String as PropType<getStat_stat>, default: 'timems' },
    sortDesc: { type: Boolean, default: false },
    displayBy: { type: String as PropType<getStat_stat>, default: 'time' },
    colorTheme: { type: Object as PropType<PiecewiseColorScheme>, default: new PiecewiseColorScheme([], []) },
    softwareFilter: { type: Array<MS_Software>, default: () => [...MS_Softwares] },
    showIcon: { type: String as PropType<'' | 'software' | 'state'>, default: '' },
    newThresh: { type: Number, default: 1 },
    newDateField: { type: String as PropType<'upload_time' | 'end_time'>, default: 'upload_time' },
});
const emit = defineEmits<{ select: [] }>();

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

const cellStyle = computed(() => {
    if (bestIndex.value === -1) return props.colorTheme.getStyle(NaN);
    return props.colorTheme.getStyle(props.videos[bestIndex.value][props.displayBy]);
});

const isNew = computed(() => {
    if (bestIndex.value === -1) return false;
    const time = props.videos[bestIndex.value][props.newDateField];
    if (!time) return false;
    return globalNow.value.getTime() - time.getTime() < props.newThresh * fullDay;
});
</script>

<style lang="less" scoped>
.cell {
    outline-style: solid;
    outline-width: 1px;
    outline-color: var(--ui-border-color-lighter);
    text-align: center;
    align-items: center;
    box-sizing: border-box;
}

.cell-new {
    font-weight: 1000;
}

.video-cell-action {
    --button-accent: currentColor;
}

.cell-select {
    width: 100%;
    height: 100%;
    padding: 0;
    font-weight: inherit;
}

.cell-selected {
    outline: 2px solid var(--ui-color-primary);
    outline-offset: -1px;
    position: relative;
    z-index: 1;
}

.cell-select:focus-visible {
    box-shadow: inset 0 0 0 1px var(--ui-text-color-primary);
}

.video-cell-action:hover,
.video-cell-action:active {
    color: inherit;
}
</style>
