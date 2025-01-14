<template>
    <tippy class="cell" :duration="0">
        <!-- <div></div> -->
        <template #content>
            {{ toISODateString(date) }}
        </template>
    </tippy>
</template>

<script setup lang="ts">
import { toISODateString } from '@/utils/datetime';
import { VideoAbstract } from '@/utils/videoabstract';
import { useDark } from '@vueuse/core';
import { computed, ref, toRaw, watch } from 'vue';
import { Tippy } from 'vue-tippy';

const prop = defineProps({
    date: { type: Date, required: true },
    videos: { type: Array<VideoAbstract>, default: [] },
    bmax: { type: Number, default: 5, },
    imax: { type: Number, default: 5, },
    emax: { type: Number, default: 5, },
    size: { type: Number, default: 12 },
    cornerRadius: { type: Number, default: 2 },
    margin: { type: Number, default: 2 },
    xOffset:{type:Number,default:0},
    yOffset:{type:Number,default:0},
})

const isDark = useDark();

const count = ref({ b: 0, i: 0, e: 0, });
const red = ref(0);
const green = ref(0);
const blue = ref(0);

watch(prop, () => {
    count.value.b = 0;
    count.value.i = 0;
    count.value.e = 0;
    for (let video of prop.videos) {
        count.value[video.level]++;
    }
    red.value = count.value.b / prop.bmax;
    green.value = count.value.i / prop.imax;
    blue.value = count.value.e / prop.emax;
},{immediate: true})

</script>

<style lang="less" scoped>
.cell {
    position: absolute;
    top: v-bind("prop.yOffset * (prop.size+prop.margin) + prop.margin + 'px'");
    left: v-bind("prop.xOffset * (prop.size+prop.margin) + prop.margin + 'px'");
    width: v-bind("prop.size + 'px'");
    height: v-bind("prop.size + 'px'");
    border-radius: v-bind("prop.cornerRadius + 'px'");
    border-style: solid;
    border-color: v-bind("isDark ? '#333' : '#ccc'");
    border-width: 1px;
    background: rgb(v-bind("255 * (isDark ? red : 1-red)"), v-bind("255 * (isDark ? green : 1-green)"), v-bind("255 * (isDark ? blue : 1-blue)"));
}
</style>