<template>
    <div style="margin: auto;text-align: center;width: 888px;">
        <v-chart style="height: 240px;width: 888px;" class="chart" :option="option_cpu" autoresize />
        <v-chart style="height: 240px;width: 888px;" class="chart" :option="option_s" autoresize />
        <v-chart style="height: 240px;width: 888px;" class="chart" :option="option_r" autoresize />
        <v-chart style="height: 430px;" class="chart" :option="option_disk" autoresize />
    </div>
</template>

<script setup lang="ts">
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart, LineChart, LineSeriesOption,BarChart } from 'echarts/charts';
import {
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent,
    GridComponentOption,
    PolarComponent,

} from 'echarts/components';
import VChart, { THEME_KEY } from 'vue-echarts';
import { ref, provide } from 'vue';
import { onMounted, onBeforeUnmount, Ref, defineAsyncComponent, computed } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();


const io_cpus = ref({
    s: ["0"],
    r: ["0"],
    c: ["0"],
});
let timer: number;


onMounted(() => {
    refresh_data();
    timer = setInterval(refresh_data, 5001);

    proxy.$axios.get('/monitor/capacity/')
        .then(function (response) {
            const data = response.data;
            option_disk.value.series[0].data[0] = +data.v/1000000;
            option_disk.value.series[1].data[1] = +data.d_u/1000000;
            option_disk.value.series[2].data[1] = (+data.d_t-(+data.d_u))/1000000;
            option_disk.value.angleAxis.max = +data.d_t/1000000;
            const a = `录像大小(${Math.round(data.v/1000000)}MB)`;
            const b = `已用空间(${Math.round(data.d_u/1000000)}MB)`;
            const c = `可用空间(${Math.round((+data.d_t-(+data.d_u))/1000000)}MB)`;
            option_disk.value.series[0].name = a;
            option_disk.value.series[1].name = b;
            option_disk.value.series[2].name = c;
            option_disk.value.legend.data = [a, b, c];
        })

})

onBeforeUnmount(() => {
    // 组件即将卸载前停止定时任务  
    clearInterval(timer);

},)


// 更新曲线用的数据
const refresh_data = () => {
    proxy.$axios.get('/monitor/io_cpus/')
        .then(function (response) {
            const data = response.data;
            io_cpus.value = {
                s: data.s,
                r: data.r,
                c: data.c
            };
            option_cpu.value.series[0].data = [...io_cpus.value.c.map((i) => { return +i })];
            option_s.value.series[0].data = [...io_cpus.value.s.map((i) => { return +i / 1000 })];
            option_r.value.series[0].data = [...io_cpus.value.r.map((i) => { return +i / 1000 })];


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
    PolarComponent
]);

// provide(THEME_KEY, 'dark');

const option_cpu = ref({
    title: {
        text: "CPU",
        left: "center"
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
            }
        },
    },
    series: [
        {
            data: [0],
            type: 'line',
            symbol: 'none',
            areaStyle: {}
        }
    ]
});

const option_s = ref({
    title: {
        text: "发送的数据",
        left: "center"
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
            }
        },
    },
    series: [
        {
            data: [0],
            type: 'line',
            symbol: 'none',
            areaStyle: {}
        }
    ]
});

const option_r = ref({
    title: {
        text: "收到的数据",
        left: "center"
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
            }
        },
    },
    series: [
        {
            data: [0],
            type: 'line',
            symbol: 'none',
            areaStyle: {}
        }
    ]
});


const option_disk = ref({
  angleAxis: {
    startAngle: 90,
    endAngle: -270,
    max: 100,
  },
  radiusAxis: {
    type: 'category',
    data: ['', ''],
    z: 10
  },
  polar: {},
  series: [
    {
      type: 'bar',
      data: [44, 0],
      coordinateSystem: 'polar',
      name: '录像大小(MB)',
      stack: 'a',
      emphasis: {
        focus: 'series'
      }
    },
    {
      type: 'bar',
      data: [0, 40],
      coordinateSystem: 'polar',
      name: '已用空间(MB)',
      stack: 'a',
      emphasis: {
        focus: 'series'
      }
    },
    {
      type: 'bar',
      data: [0, 20],
      coordinateSystem: 'polar',
      name: '可用空间(MB)',
      stack: 'a',
      emphasis: {
        focus: 'series'
      }
    }
  ],
  legend: {
    show: true,
    data: ['录像大小(MB)', '已用空间(MB)', '可用空间(MB)']
  }
});
</script>

<style scoped>
.chart {
    height: 100vh;
}
</style>