<template>
    <tippy class="cell" :duration="0" sticky>
        <template v-if="bestIndex == -1">
&nbsp;
        </template>
        <el-link v-else :underline="false" @click="preview(videos[bestIndex].id)">
            {{ videos[bestIndex].displayStat(displayBy) }}
        </el-link>
        <template #content>
            <base-card-small v-if="bestIndex >= 0">
                上传时间：{{ videos[bestIndex].upload_time }}<br>
                共计：{{ videos.length }} 个视频<br>
            </base-card-small>
        </template>
    </tippy>
</template>

<script setup lang="ts">
import { BBBvSummaryConfig } from '@/store';
import { VideoAbstract, getStat_stat } from '@/utils/videoabstract';
import { computed, PropType, ref, watch } from 'vue';
import { Tippy } from 'vue-tippy';
import { ElLink } from 'element-plus';
import { MS_Level, MS_Software, MS_Softwares } from '@/utils/ms_const';
import { PiecewiseColorScheme } from '@/utils/colors';
import tinycolor from 'tinycolor2';
import { preview } from '@/utils/common/PlayerDialog';
import BaseCardSmall from '@/components/common/BaseCardSmall.vue';

const bestValue = ref<number|null>(null);
const bestIndex = ref(-1);

const prop = defineProps({
    level: { type: String as PropType<MS_Level>, required: true },
    bv: { type: Number, required: true },
    videos: { type: Array<VideoAbstract>, default: [] },
    sortBy: { type: String as PropType<getStat_stat>, default: 'timems' },
    sortDesc: { type: Boolean, default: false },
    displayBy: { type: String as PropType<getStat_stat>, default: 'time' },
    colorTheme: { type: Object as PropType<PiecewiseColorScheme>, default: new PiecewiseColorScheme([],[])},
    softwareFilter: { type: Array<MS_Software>, default: () => [...MS_Softwares]},
})

function refresh() {
    bestValue.value = null;
    bestIndex.value = -1;
    prop.videos.forEach((video, index) => {
        if (!prop.softwareFilter.includes(video.software)) return;
        const thisValue = video.getStat(prop.sortBy);
        if (thisValue === undefined) return;
        if (
            bestValue.value === null ||
            thisValue > bestValue.value && prop.sortDesc ||
            thisValue < bestValue.value && !prop.sortDesc
        ) {
            bestValue.value = thisValue;
            bestIndex.value = index;
        }
    });
}

watch(prop, refresh, { immediate: true });

const height = computed(() => BBBvSummaryConfig.value.cellHeight + 'px');

const color = computed(() => {
    if (bestIndex.value === -1) return 'rgba(0,0,0,0)';
    return prop.colorTheme.getColor(prop.videos[bestIndex.value].getStat(prop.displayBy) as number)
})

const fontColor = computed(() => tinycolor(color.value).isDark() ? 'white' : 'black');

</script>

<style lang="less" scoped>

.cell {
    display: inline-block;
    height: v-bind(height);
    background-color: v-bind(color);
    outline-style: solid;
    outline-width: 1px;
    text-align: center;
    align-items: center;
    box-sizing: border-box;
}

.el-link {
    --el-link-text-color: v-bind(fontColor);
    --el-link-font-size: 16px;
}

</style>