<template>
    <el-card style="overflow: auto;">
        <div style="align-items: center; display: flex;">
            <el-segmented v-model="year" :options="[2024,2025]" size="small" style="font-size: 12px"/>
            <span style="flex: 1;"></span>
            <el-text size="small">{{ t('msg.totalNVideos', [count]) }}</el-text>
            <span style="width: 10px;"></span>
            <el-checkbox-group v-model="level" size="small">
                <el-checkbox-button v-for="l in ['b', 'i', 'e']" :value="l">
                    {{ t('common.level.' + l) }}
                </el-checkbox-button>
            </el-checkbox-group>
        </div>
        <v-chart :option="option" class="chart"
            :init-options="{ locale: local.language == 'zh-cn' ? 'ZH' : 'EN' }" :theme="isDark ? 'dark' : 'light'" autoresize/>
    </el-card>
</template>

<script setup lang="ts">

import { computed, ref, watch } from 'vue';
import VChart from 'vue-echarts';
import * as echarts from 'echarts/core';
import { HeatmapChart } from 'echarts/charts';
import { CanvasRenderer } from 'echarts/renderers';
import { CalendarComponent, VisualMapComponent, TooltipComponent } from 'echarts/components';
import { store, local } from '@/store';
import { useDark } from '@vueuse/core';
import { useI18n } from 'vue-i18n';

const isDark = useDark();
const { t } = useI18n();

echarts.use([
    CalendarComponent,
    VisualMapComponent,
    HeatmapChart,
    CanvasRenderer,
    TooltipComponent
]);

const year = ref(2024);
const level = ref(['b', 'i', 'e']);
const count = ref(0);

const getData = (videos: Array<any>, year: string | number, level: Array<string>) => {
    const data = [] as Array<[string, number]>;
    const date = +echarts.number.parseDate(year + '-01-01');
    const end = +echarts.number.parseDate(year + '-12-31');
    let thiscount = 0;
    for (let time = date; time <= end; time += 3600 * 24 * 1000) {
        data.push([
            echarts.time.format(time, '{yyyy}-{MM}-{dd}', false),
            0
        ]);
    }
    for (let video of videos) {
        if (!level.includes(video.level)) {
            continue;
        }
        let video_date = +echarts.number.parseDate(video.upload_time);
        let date_index = Math.floor((video_date - date) / (3600 * 24 * 1000));
        if (date_index >= 0 && date_index < data.length) {
            data[date_index][1] += 1;
            thiscount += 1;
        }
    }
    count.value = thiscount;
    return data;
}

const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--el-color-primary');

const option = computed(() => {
    return {
        visualMap: {
            show: false,
            min: 0,
            max: 10,
            inRange: {
                color: isDark.value ? ['#333', primaryColor] : ['#ccc', primaryColor]
            }
        },
        calendar: {
            top: 25,
            bottom: 5,
            left: 25,
            right: 5,
            range: year.value,
            cellsize: ['auto', 'auto'],
            splitLine: {
                show: false,
                lineStyle: {
                    width: 1.5,
                    join: 'round',
                },
            },
            itemStyle: {
                borderColor: isDark.value ? '#000' : '#fff',
                borderWidth: 2,
                borderJoin: 'round',
            },
            dayLabel: {
                fontSize: 7,
            },
            monthLabel: {
                fontSize: 10,
            }
        },
        tooltip: {
            textStyle: {
                fontSize: 10,
            },
            padding: 3,
            formatter: (p: any) => {
                return t('msg.uploadedNVideosOnDate', p.value);
            },
        },
        series: [
            {
                type: 'heatmap',
                coordinateSystem: 'calendar',
                data: getData(store.player.videos, year.value, level.value),
                itemStyle: {
                    borderRadius: 3,
                },
            }
        ]
    }
})

</script>

<style scoped lang="less">
.chart {
    height: 110px;
    width: 100%;
}

::v-deep(.el-checkbox-button:first-child .el-checkbox-button__inner) {
    border-top-left-radius: 1px;
    border-bottom-left-radius: 1px;
}

::v-deep(.el-checkbox-button:last-child .el-checkbox-button__inner) {
    border-top-right-radius: 1px;
    border-bottom-right-radius: 1px;
}

::v-deep(.el-checkbox-button--small .el-checkbox-button__inner) {
    padding: 5px 8px;
    font-size: 10px;
}

</style>