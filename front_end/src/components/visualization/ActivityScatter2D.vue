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
import { getStat_stat, VideoAbstract } from '@/utils/videoabstract';
import { MS_Levels } from '@/utils/ms_const';
import { ElCard } from 'element-plus';

const video_stats = ['time', 'bv', 'bvs']

const { t } = useI18n();

echarts.use([ScatterChart])

const level = ref([...MS_Levels]);
const x = ref<getStat_stat>('time');
const y = ref<getStat_stat>('bv');

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
            ).map((video: VideoAbstract) => {
                return [video.getStat(x.value), video.getStat(y.value), video];
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