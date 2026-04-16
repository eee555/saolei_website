<template>
    <div style="width: 10%; min-width: 75px; text-align: center">
        <div v-for="i of ArrayUtils.range(minBv, maxBv, 10)" :key="i" class="text" :style="{width: '100%', lineHeight: '25px'}">
            {{ i }}-{{ i+9 }}
        </div>
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ArrayUtils } from '@/utils/arrays';

defineProps({
    minBv: { type: Number, required: true },
    maxBv: { type: Number, required: true },
});

</script>
