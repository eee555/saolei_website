<template>
    <!-- @vue-ignore -->
    <RangeSlider v-model="videofilter.bbbv_range[level]" :min="minbvlim[level]" :max="maxbvlim[level]" />
</template>

<script setup lang="ts">

import { videofilter } from '@/store';
import RangeSlider from '../RangeSlider.vue';

defineProps({
    level: {
        type: String,
        default: 'e',
    },
});

const minbvlim = {
    'b': 1,
    'i': 1,
    'e': 1,
};

const maxbvlim = {
    'b': 54,
    'i': 216,
    'e': 381,
};

</script>
