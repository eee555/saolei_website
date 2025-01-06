<template>
    <el-card>
        <div style="align-items: center; display: flex;">
            <span style="flex: 1;"></span>
            <MSStatSelect v-model="stat_show" :options="['time', 'bvs']" style="width: 100px" />
        </div>
        <v-chart v-if="level_visible.includes('b')" :option="getOption(store.player.videos, 'b', stat_show)" :style="{ height: heights.b + 30 + 'px', width: '100%' }"
            autoresize @click="handleClick" />
        <v-chart v-if="level_visible.includes('i')" :option="getOption(store.player.videos, 'i', stat_show)" :style="{ height: heights.i + 'px', width: '100%' }"
            autoresize @click="handleClick" />
        <v-chart v-if="level_visible.includes('e')" :option="getOption(store.player.videos, 'e', stat_show)" :style="{ height: heights.e + 'px', width: '100%' }"
            autoresize @click="handleClick" />
    </el-card>
</template>

<script setup lang="ts">
import { colorTheme, store } from '@/store';
import { getStat_stat, VideoAbstract } from '@/utils/fileIO';
import VChart from 'vue-echarts';
import * as echarts from 'echarts/core';
import { HeatmapChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, VisualMapComponent } from 'echarts/components';
import { range } from '@/utils/arrays';
import { useDark } from '@vueuse/core';
import { preview } from '@/utils/common/PlayerDialog';
import { ref } from 'vue';
import { deepCopy } from '@/utils';
import MSStatSelect from '../Filters/MSStatSelect.vue';
import { useI18n } from 'vue-i18n';

const isDark = useDark();
const { t } = useI18n();

echarts.use([
    HeatmapChart,
    VisualMapComponent,
    TooltipComponent,
    GridComponent,
])

const level_visible = ref(['b', 'i', 'e']);
const stat_show = ref<'time' | 'bvs'>('time');

const pb_index_all = {
    b: new Array<number | null>(54).fill(null),
    i: new Array<number | null>(216).fill(null),
    e: new Array<number | null>(381).fill(null),
};

const heights = {
    b: 100,
    i: 100,
    e: 100,
}

function getPBindex(videos: Array<VideoAbstract>, stat: getStat_stat, smallIsBetter: boolean, level: 'b' | 'i' | 'e') {
    let pb_index = pb_index_all[level];
    pb_index.fill(null);
    let pb = deepCopy(pb_index);
    for (let i = 0; i < videos.length; i++) {
        if (videos[i].level != level) continue;
        let value = videos[i].getStat(stat);
        if (value == null) continue;
        let bv = videos[i].bv;
        let pb_value = pb[bv - 1];
        if (pb_value == null || smallIsBetter && value < pb_value || !smallIsBetter && value > pb_value) {
            pb[bv - 1] = value;
            pb_index[bv - 1] = i;
        }
    }
}

const columns = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

function getPBFirstRow(pb_index: Array<number | null>) {
    let firstindex = pb_index.findIndex((value) => value != null);
    return Math.floor((firstindex + 1) / 10);
}

function getPBLastRow(pb_index: Array<number | null>) {
    let lastindex = pb_index.findLastIndex((value) => value != null);
    return Math.floor((lastindex + 1) / 10);
}

function getPBrows(pb_index: Array<number | null>) {
    return range(getPBFirstRow(pb_index), getPBLastRow(pb_index)).map((value: number) => value * 10);
}

function getPBheatmap(videos: Array<VideoAbstract>, pb_index: Array<number | null>, stat: getStat_stat, yOffset: number = 0) {
    let data = [] as Array<[number, number, number, VideoAbstract]>;
    let offset = yOffset - getPBFirstRow(pb_index);
    for (let i = 0; i < pb_index.length; i++) {
        let index = pb_index[i];
        if (index == null) continue;
        let bv = i + 1;
        data.push([bv % 10, Math.floor(bv / 10) + offset, videos[index].getStat(stat), videos[index]]);
    }
    return data;
}

function getSplitLineStyle() {
    return {
        color: isDark.value ? '#333' : '#ccc',
    }
}

function getHeight(pb_index: Array<number | null>) {
    return 30 * (getPBLastRow(pb_index) - getPBFirstRow(pb_index) + 1);
}

function getPieces(level: 'b' | 'i' | 'e', stat: 'time' | 'bvs') {
    let thresholds;
    let colors;
    if (stat === 'bvs') {
        thresholds = colorTheme.value.bvs.thresholds;
        colors = colorTheme.value.bvs.colors;
    } else if (stat === 'time') {
        if (level === 'b') {
            thresholds = colorTheme.value.btime.thresholds;
            colors = colorTheme.value.btime.colors;
        } else if (level === 'i') {
            thresholds = colorTheme.value.itime.thresholds;
            colors = colorTheme.value.itime.colors;
        } else { // if (level === 'e')
            thresholds = colorTheme.value.etime.thresholds;
            colors = colorTheme.value.etime.colors;
        }
    } else {
        thresholds = colorTheme.value.stnb.thresholds;
        colors = colorTheme.value.stnb.colors;
    }
    let pieces = [{
        max: thresholds[0],
        color: colors[0],
    }] as Array<any>;
    for (let i = 0; i < thresholds.length - 1; i++) {
        pieces.push({
            min: thresholds[i],
            max: thresholds[i + 1],
            color: colors[i + 1],
        })
    }
    pieces.push({
        min: thresholds[thresholds.length - 1],
        color: colors[colors.length - 1],
    })
    return pieces;
}

const getOption = (videos: Array<VideoAbstract>, level: 'b' | 'i' | 'e', stat: 'time' | 'bvs') => {
    getPBindex(videos, 'time', true, level);
    heights[level] = getHeight(pb_index_all[level]);
    return {
        xAxis: {
            type: 'category',
            data: columns,
            position: 'top',
            splitLine: {
                show: true,
                lineStyle: getSplitLineStyle(),
            },
            axisLine: {
                show: level === 'b',
            },
            axisLabel: {
                show: level === 'b',
            },
            axisTick: {
                show: level === 'b',
            },
        },
        yAxis: {
            type: 'category',
            data: getPBrows(pb_index_all[level]),
            inverse: true,
            splitLine: {
                show: true,
                lineStyle: getSplitLineStyle(),
            },
        },
        grid: {
            show: true,
            top: 30,
            bottom: 0,
            left: 30,
            right: 0,
        },
        visualMap: {
            show: false,
            type: 'piecewise',
            pieces: getPieces(level, stat),
            dimension: 2,
        },
        series: [
            {
                type: 'heatmap',
                label: {
                    show: true,
                    formatter: (v: any) => v.data[2].toFixed(3),
                },
                data: getPBheatmap(videos, pb_index_all[level], stat),
            },
        ],
        tooltip: {
            show: true,
            formatter: (p: any) => {
                let video = new VideoAbstract(p.data[3]);
                return video.tooltipFormatter(t);
            },
        }
    }
}

const handleClick = (params: any) => {
    preview(params.data[3].id);
}

</script>

<style lang="less" scoped>
.chart {
    aspect-ratio: 2;
    width: 100%;
}

.el-card {
    --el-card-padding: 10px;
}
</style>