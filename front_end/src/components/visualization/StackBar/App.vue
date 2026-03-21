<template>
    <div style="height: 0.3em; display: flex; align-items: center;">
        <base-tooltip v-for="(item, index) in data" :key="item.name" :data-cy="item.name" :show-delay="200" :style="{ width: `${(item.value / sumValue * 100)}%`, height: '100%', background: item.color, borderTopLeftRadius: index === 0 ? '0.1em' : '0', borderBottomLeftRadius: index === 0 ? '0.1em' : '0', borderTopRightRadius: index === prop.data.length - 1 ? '0.1em' : '0', borderBottomRightRadius: index === prop.data.length - 1 ? '0.1em' : '0'}">
            <template #content>
                <el-text>
                    {{ item.name }}: {{ (item.value / sumValue * 100).toFixed(0) }}%({{ item.value }})
                </el-text>
            </template>
        </base-tooltip>
    </div>
    <div v-if="legend">
        <span v-for="item in data" :key="item.name" style="margin: 0 0.2em">
            <template v-if="item.value > 0">
                <span class="dot" :style="{ background: item.color }" />
                <span class="text-normal">
                    {{ item.name }}: {{ (item.value / sumValue * 100).toFixed(0) }}%({{ item.value }})
                </span>
            </template>
        </span>
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { sum } from 'd3-array';
import { ElText } from 'element-plus';
import { computed } from 'vue';

import BaseTooltip from '@/components/common/BaseTooltip.vue';

interface DataItem {
    name: string;
    value: number;
    color: string;
}

const prop = defineProps({
    data: {
        type: Array<DataItem>,
        default: () => [],
    },
    legend: { type: Boolean, default: false },
});

const sumValue = computed(() => sum(prop.data, (item) => item.value));

</script>

<style lang="less" scoped>
.dot {
    width: 0.75em;
    height: 0.75em;
    border-radius: 50%;
    display: inline-block;
    vertical-align: middle;
}
</style>
