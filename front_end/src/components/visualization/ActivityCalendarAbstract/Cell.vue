<template>
    <Tippy class="cell" :duration="0" sticky>
        <el-text
            v-if="showDate" :style="{
                position: 'absolute',
                top: `${cellSize / 2}px`,
                left: `${cellSize / 2}px`,
                transform: 'translate(-50%, -50%)',
                fontSize: `${cellSize * 0.6}px`,
            }"
        >
            <!-- 用class的情况下不知为何字号不会生效 -->
            {{ date.getDate() }}
        </el-text>
        <template #content>
            <!-- vue-tippy的bug，改语言的时候content不会刷新，不算大问题就不用workaround了，等上游修复 -->
            <base-card-small>
                <el-text v-if="videos.length == 0">
                    {{ t('activityCalendar.tooltip.noVideoOnDate', [toISODateString(date)]) }}
                </el-text>
                <template v-else>
                    <el-text>{{ t('activityCalendar.tooltip.uploadedNVideosOnDate', [toISODateString(date), videos.length]) }}</el-text>
                    <br>
                    <span v-for="i in count.b" :key="i" class="dot" style="background-color: #f00;" />
                    <span v-for="i in count.i" :key="i" class="dot" style="background-color: #080;" />
                    <span v-for="i in count.e" :key="i" class="dot" style="background-color: #00f;" />
                </template>
            </base-card-small>
        </template>
    </Tippy>
</template>

<script setup lang="ts">
import { toISODateString } from '@/utils/datetime';
import { VideoAbstract } from '@/utils/videoabstract';
import { computed, ref, watch } from 'vue';
import { Tippy } from 'vue-tippy';
import { ElText } from 'element-plus';
import BaseCardSmall from '@/components/common/BaseCardSmall.vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const prop = defineProps({
    date: { type: Date, required: true },
    videos: { type: Array<VideoAbstract>, default: [] }, // 该日期的录像
    bmax: { type: Number, default: 5 },
    imax: { type: Number, default: 5 },
    emax: { type: Number, default: 5 }, // 三个最大值，用于计算颜色
    xOffset: { type: Number, default: 0 }, // 横坐标，单位为格
    yOffset: { type: Number, default: 0 }, // 纵坐标，单位为格
    cellSize: { type: Number, default: 14 }, // 格子大小，单位为px
    cellMargin: { type: Number, default: 3 }, // 格子间距，单位为px
    showDate: { type: Boolean, default: true }, // 是否显示日期
    cornerRadius: { type: Number, default: 20 }, // 圆角，单位为%
});

const count = ref({ b: 0, i: 0, e: 0 });
const red = ref(0);
const green = ref(0);
const blue = ref(0);

function refresh() {
    count.value.b = 0;
    count.value.i = 0;
    count.value.e = 0;
    for (const video of prop.videos) {
        count.value[video.level]++;
    }
    red.value = 255 * count.value.b / prop.bmax;
    green.value = 255 * count.value.i / prop.imax;
    blue.value = 255 * count.value.e / prop.emax;
}

watch(() => prop.videos, refresh, { immediate: true });

const size = computed(() => prop.cellSize + 'px');
const borderRadius = computed(() => prop.cornerRadius + '%');
const top = computed(() => prop.yOffset * (prop.cellSize + prop.cellMargin) + prop.cellMargin + 'px');
const left = computed(() => prop.xOffset * (prop.cellSize + prop.cellMargin) + prop.cellMargin + 'px');

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
</style>
