<template>
    <div style="width: 10%; min-width: 75px; text-align: center">
        <div v-for="i of ArrayUtils.range(minBv, maxBv, 10)" :style="{width: '100%', lineHeight:`${BBBvSummaryConfig.cellHeight}px`}">
            {{ i }}-{{ i+9 }}
        </div>
    </div>
</template>

<script setup lang="ts">
import { BBBvSummaryConfig } from '@/store';
import { ArrayUtils } from '@/utils/arrays';


defineProps({
    minBv: { type: Number, required: true },
    maxBv: { type: Number, required: true },
});

</script>
