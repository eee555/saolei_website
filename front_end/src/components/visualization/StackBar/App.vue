<template>
    <div style="height: 0.3em; display: flex; align-items: center;">
        <base-tooltip v-for="(item, index) in prop.data" :key="item.name" :data-cy="item.name" :show-delay="200" :style="{ width: `${(item.value / sumValue * 100)}%`, height: '100%', background: item.color, borderTopLeftRadius: index === 0 ? '0.1em' : '0', borderBottomLeftRadius: index === 0 ? '0.1em' : '0', borderTopRightRadius: index === prop.data.length - 1 ? '0.1em' : '0', borderBottomRightRadius: index === prop.data.length - 1 ? '0.1em' : '0'}">
            <template #content>
                <el-text>
                    {{ item.name }}: {{ (item.value / sumValue * 100).toFixed(0) }}%({{ item.value }})
                </el-text>
            </template>
        </base-tooltip>
    </div>
</template>

<script setup lang="ts">

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
});

const sumValue = computed(() => sum(prop.data, (item) => item.value));

</script>
