<template>
    <el-card>
        <div style="align-items: center; display: flex;">
            <MSLevelFilter v-model="level" />
            <span style="flex: 1;"></span>
            <MSStatSelect v-model="x" label="x" :options="video_stats" />
            <span style="width: 10px;"></span>
            <MSStatSelect v-model="y" label="y" :options="video_stats" />
        </div>
        <v-chart class="chart" :option="option" autoresize @click="handleClick" />
    </el-card>

</template>

<script setup lang="ts">

import VChart from 'vue-echarts';
import { store } from '@/store';
import * as echarts from 'echarts/core';
import { ScatterChart } from 'echarts/charts';
import { computed, ref } from 'vue';
import MSLevelFilter from '../Filters/MSLevelFilter.vue';
import { preview } from '@/utils/common/PlayerDialog';
import { useI18n } from 'vue-i18n';
import MSStatSelect from '../Filters/MSStatSelect.vue';

const video_stats = ['time', 'bv', 'bvs']

const { t } = useI18n();

echarts.use([ScatterChart])

const level = ref(['b', 'i', 'e']);
const x = ref('time');
const y = ref('bv');

function getStat(video: any, stat: string) {
    switch (stat) {
        case 'time':
            return video.timems / 1000;
        case 'bv':
            return video.bv;
        case 'bvs':
            return video.timems == 0 ? 0 : video.bv / video.timems * 1000;
        default:
            return null;
    }
}

const option = computed(() => {
    return {
        xAxis: {
            name: t('common.prop.' + x.value),
            nameLocation: 'center',
            nameGap: 20,
            splitLine: {
                lineStyle: {
                    color: '#333',
                },
            },
        },
        yAxis: {
            name: t('common.prop.' + y.value),
            nameLocation: 'center',
            nameGap: 30,
            splitLine: {
                lineStyle: {
                    color: '#333',
                },
            },
        },
        grid: {
            top: 15,
            left: 50,
            right: 15,
            bottom: 30,
        },
        series: {
            type: 'scatter',
            data: store.player.videos.filter(
                (video) => level.value.includes(video.level)
            ).map((video) => {
                return [getStat(video,x.value), getStat(video,y.value), video];
            }),
        },
        tooltip: {
            formatter: (p: any) => {
                return `Time: ${p.data[2].timems/1000}<br>BBBV: ${p.data[2].bv}<br>Level: ${t('common.level.'+p.data[2].level)}`;
            }
        }
    }
})

const handleClick = (params: any) => {
    preview(params.data[2].id);
}

</script>

<style scoped lang="less">
.chart {
    height: 300px;
    width: 100%;
}

.el-select {
    width: 80px;
}

.el-card {
    --el-card-padding: 10px;
}
</style>