<template>
    <tippy class="cell" :duration="0">
        <!-- <div></div> -->
        <template #content>
            {{ date.toISOString().split('T')[0] }}
        </template>
    </tippy>
</template>

<script setup lang="ts">
import { VideoAbstract } from '@/utils/videoabstract';
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
    red.value = 255 * count.value.b / prop.bmax;
    green.value = 255 * count.value.i / prop.imax;
    blue.value = 255 * count.value.e / prop.emax;
},{immediate: true})

const top = computed(() => prop.yOffset * (prop.size+prop.margin) + prop.margin + 'px');
const left = computed(() => prop.xOffset * (prop.size+prop.margin) + prop.margin + 'px');
const sizeString = computed(() => prop.size + 'px');
const borderRadiusString = computed(() => prop.cornerRadius + 'px');

</script>

<style lang="less" scoped>
.cell {
    position: absolute;
    top: v-bind(top);
    left: v-bind(left);
    width: v-bind(sizeString);
    height: v-bind(sizeString);
    border-radius: v-bind(borderRadiusString);
    background: rgb(v-bind(red), v-bind(green), v-bind(blue));
}
</style>