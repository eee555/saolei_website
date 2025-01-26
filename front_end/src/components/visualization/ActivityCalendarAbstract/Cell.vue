<template>
    <Tippy class="cell" :duration="0" sticky>
        <el-text v-if="activityCalendarConfig.showDate" :style="{
            position: 'absolute',
            top: activityCalendarConfig.cellSize / 2 + 'px',
            left: activityCalendarConfig.cellSize / 2 + 'px',
            transform: 'translate(-50%, -50%)',
            fontSize: activityCalendarConfig.cellSize * 0.6 + 'px',
        }"> <!-- 用class的情况下不知为何字号不会生效 -->
            {{ date.getDate() }}
        </el-text>
        <template #content>
            <!-- vue-tippy的bug，改语言的时候content不会刷新，不算大问题就不用workaround了，等上游修复 -->
            <el-card>
            <el-text v-if="videos.length == 0" v-t="{path: 'activityCalendar.tooltip.noVideoOnDate', args: [toISODateString(date)]}" />
            <template v-else>
                <el-text
                    v-t="{ path: 'activityCalendar.tooltip.uploadedNVideosOnDate', args: [toISODateString(date), videos.length] }" />
                <br>
                <span v-for="i in count.b" class="dot" style="background-color: #f00;"></span>
                <span v-for="i in count.i" class="dot" style="background-color: #080;"></span>
                <span v-for="i in count.e" class="dot" style="background-color: #00f;"></span>
            </template>
        </el-card>
        </template>
    </Tippy>
</template>

<script setup lang="ts">
import { activityCalendarConfig, local } from '@/store';
import { toISODateString } from '@/utils/datetime';
import { VideoAbstract } from '@/utils/videoabstract';
import { computed, ref, toRaw, watch } from 'vue';
import { Tippy } from 'vue-tippy';
import { ElText, ElCard } from 'element-plus';

const prop = defineProps({
    date: { type: Date, required: true },
    videos: { type: Array<VideoAbstract>, default: [] },
    bmax: { type: Number, default: 5, },
    imax: { type: Number, default: 5, },
    emax: { type: Number, default: 5, },
    xOffset: { type: Number, default: 0 },
    yOffset: { type: Number, default: 0 },
})

const count = ref({ b: 0, i: 0, e: 0, });
const red = ref(0);
const green = ref(0);
const blue = ref(0);

watch(() => prop.videos, () => {
    count.value.b = 0;
    count.value.i = 0;
    count.value.e = 0;
    for (let video of prop.videos) {
        count.value[video.level]++;
    }
    red.value = 255 * count.value.b / prop.bmax;
    green.value = 255 * count.value.i / prop.imax;
    blue.value = 255 * count.value.e / prop.emax;
})

const size = computed(() => activityCalendarConfig.value.cellSize + 'px');
const borderRadius = computed(() => activityCalendarConfig.value.cornerRadius + '%');
const top = computed(() => prop.yOffset * (activityCalendarConfig.value.cellSize + activityCalendarConfig.value.cellMargin) + activityCalendarConfig.value.cellMargin + 'px');
const left = computed(() => prop.xOffset * (activityCalendarConfig.value.cellSize + activityCalendarConfig.value.cellMargin) + activityCalendarConfig.value.cellMargin + 'px');

</script>

<style lang="less" scoped>
.cell {
    position: absolute;
    top: v-bind(top);
    left: v-bind(left);
    width: v-bind(size);
    height: v-bind(size);
    border-radius: v-bind(borderRadius);
    border-style: solid;
    border-color: #333;
    border-width: 1px;
    background: rgb(v-bind(red), v-bind(green), v-bind(blue));
}

.dot {
    height: 12px;
    width: 12px;
    border-radius: 50%;
    display: inline-block;
}

.el-card {
    --el-card-padding: 5px;
}
</style>