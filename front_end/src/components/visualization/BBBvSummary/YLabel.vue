<template>
    <div style="width: 10%; min-width: 75px; text-align: center">
        <el-text v-for="i of ArrayUtils.range(minBv, maxBv, 10)" :key="i" tag="div" :style="{width: '100%', lineHeight: '25px'}">
            {{ i }}-{{ i+9 }}
        </el-text>
    </div>
</template>

<script setup lang="ts">
import { ArrayUtils } from '@/utils/arrays';
import { ElText } from 'element-plus';

defineProps({
    minBv: { type: Number, required: true },
    maxBv: { type: Number, required: true },
});

</script>
