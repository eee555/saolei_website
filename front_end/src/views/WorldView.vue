<template>
    <div style="margin: auto;text-align: center;width: 888px;">
        <v-chart style="height: 240px;width: 888px;" class="chart" :option="option_cpu" autoresize />
        <v-chart style="height: 240px;width: 888px;" class="chart" :option="option_s" autoresize />
        <v-chart style="height: 240px;width: 888px;" class="chart" :option="option_r" autoresize />
        <v-chart style="height: 328px;" class="chart" :option="option_disk" autoresize />
        <v-chart style="height: 328px;" class="chart" :option="option_virtual_memory" autoresize />
    </div>
</template>

<script setup lang="ts">
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart, LineChart, BarChart } from 'echarts/charts';
import {
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent,
    PolarComponent,

} from 'echarts/components';
import VChart from 'vue-echarts';
import { ref } from 'vue';
import { onMounted, onBeforeUnmount } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();


const io_cpus = ref({
    s: ["0"],
    r: ["0"],
    c: ["0"],
});
let timer_1: number;
let timer_2: number;


onMounted(() => {
    refresh_data();
    timer_1 = setInterval(refresh_data, 5010);
    refresh_memory_data();
    timer_2 = setInterval(refresh_memory_data, 188010);
})

onBeforeUnmount(() => {
    // 组件即将卸载前停止定时任务  
    clearInterval(timer_1);
    clearInterval(timer_2);

})


// 更新曲线用的数据
const refresh_data = () => {
    proxy.$axios.get('/monitor/io_cpus/').
        then(function (response) {
            const data = response.data;
            io_cpus.value = {
                s: data.s,
                r: data.r,
                c: data.c,
            };
            option_cpu.value.series[0].data = [...io_cpus.value.c.map((i) => { return +i })];
            option_s.value.series[0].data = [...io_cpus.value.s.map((i) => { return +i / 1000 })];
            option_r.value.series[0].data = [...io_cpus.value.r.map((i) => { return +i / 1000 })];


        })
}

const refresh_memory_data = () => {
    proxy.$axios.get('/monitor/capacity/').
        then(function (response) {
            const data = response.data;
            option_disk.value.series[0].data[0].value = +data.v / 1000000;
            option_disk.value.series[0].endAngle = 90 - 360 * (data.v / data.d_t);
            option_disk.value.series[1].data[0].value = +data.d_u / 1000000;
            option_disk.value.series[1].data[1].value = (+data.d_t - (+data.d_u)) / 1000000;
            const a = `录像大小(${Math.round(data.v / 1000000)}MB)`;
            const b = `已用空间(${Math.round(data.d_u / 1000000)}MB)`;
            const c = `可用空间(${Math.round((+data.d_t - (+data.d_u)) / 1000000)}MB)`;
            option_disk.value.series[0].data[0].name = a;
            option_disk.value.series[1].data[0].name = b;
            option_disk.value.series[1].data[1].name = c;
            option_disk.value.legend.data = [a, b, c];
            option_virtual_memory.value.series[0].data[0].value = +data.v_u / 1000000;
            option_virtual_memory.value.series[0].data[1].value = (+data.v_t - (+data.v_u)) / 1000000;
            const d = `已用内存(${Math.round(data.v_u / 1000000)}MB)`;
            const e = `可用内存(${Math.round((+data.v_t - (+data.v_u)) / 1000000)}MB)`;
            option_virtual_memory.value.series[0].data[0].name = d;
            option_virtual_memory.value.series[0].data[1].name = e;
            option_virtual_memory.value.legend.data = [d, e];
        })
}

use([
    CanvasRenderer,
    PieChart,
    LineChart,
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent,
    BarChart,
    PolarComponent,
]);

// provide(THEME_KEY, 'dark');

const option_cpu = ref({
    title: {
        text: "CPU",
        left: "center",
    },
    xAxis: {
        type: 'category',
        boundaryGap: false,
        show: false,
        // data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    },
    yAxis: {
        min: 0,
        max: 100,
        type: 'value',
        axisLabel: {
            formatter: function (value: number) {
                return value + '%';
            },
        },
    },
    series: [
        {
            data: [0],
            type: 'line',
            symbol: 'none',
            areaStyle: {},
        },
    ],
});

const option_s = ref({
    title: {
        text: "发送的数据",
        left: "center",
    },
    xAxis: {
        type: 'category',
        boundaryGap: false,
        show: false,
        // data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    },
    yAxis: {
        min: 0,
        // max: 1000,
        type: 'value',
        axisLabel: {
            formatter: function (value: number) {
                return value + 'kB/s';
            },
        },
    },
    series: [
        {
            data: [0],
            type: 'line',
            symbol: 'none',
            areaStyle: {},
        },
    ],
});

const option_r = ref({
    title: {
        text: "收到的数据",
        left: "center",
    },
    xAxis: {
        type: 'category',
        boundaryGap: false,
        show: false,
        // data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    },
    yAxis: {
        min: 0,
        // max: 1000,
        type: 'value',
        axisLabel: {
            formatter: function (value: number) {
                return value + 'kB/s';
            },
        },
    },
    series: [
        {
            data: [0],
            type: 'line',
            symbol: 'none',
            areaStyle: {},
        },
    ],
});


const option_disk = ref({
    legend: {
        data: [
            '可用空间',
            '已用空间',
            '录像大小',
        ],
    },
    series: [
        {
            name: '录像大小',
            type: 'pie',
            selectedMode: 'single',
            radius: [0, '38%'],
            endAngle: 50,
            label: {
                show: false,
            },
            data: [{ value: 50, name: 'Search Engine' }],
        },
        {
            name: '磁盘大小',
            type: 'pie',
            radius: ['45%', '68%'],
            label: {
                show: false,
            },
            data: [
                { value: 1048, name: '已用空间' },
                { value: 335, name: '可用空间' },
            ],
        },
    ],
});


const option_virtual_memory = ref({
    legend: {
        data: [
            '已用空间',
            '可用空间',
        ],
    },
    series: [
        {
            name: '内存大小',
            type: 'pie',
            label: {
                show: false,
            },
            data: [
                { value: 1048, name: '已用空间' },
                { value: 335, name: '可用空间' },
            ],
        },
    ],
});

</script>

<style scoped>
.chart {
    height: 100vh;
}
</style>
