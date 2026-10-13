<template>
    <g :transform="`translate(${x}, ${y})`" :fill="color" :opacity="marker.opacity">
        <circle v-if="marker.shape === 'circle'" :r="half" />
        <rect v-else-if="marker.shape === 'square'" :x="-half" :y="-half" :width="marker.size" :height="marker.size" />
        <polygon v-else-if="marker.shape === 'triangle'" :points="`0,${-half} ${half},${half} ${-half},${half}`" />
        <polygon v-else-if="marker.shape === 'diamond'" :points="`0,${-half} ${half},0 0,${half} ${-half},0`" />
        <path v-else :d="`M${-half},${-half} L${half},${half} M${-half},${half} L${half},${-half}`" :stroke="color" :stroke-width="Math.max(1, marker.size / 4)" fill="none" />
    </g>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { PropType } from 'vue';

import type { CustomEventDefinition } from './customEvents';

const props = defineProps({
    x: { type: Number, required: true },
    y: { type: Number, required: true },
    color: { type: String, required: true },
    marker: { type: Object as PropType<CustomEventDefinition['marker']>, required: true },
});
const half = computed(() => props.marker.size / 2);
</script>
