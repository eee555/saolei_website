<template>
    <RangeSlider :min="minbvlim[level]" :max="maxbvlim[level]" v-model="filter.bbbv_range[level]"/>
</template>

<script setup lang="ts">

import { useVideoFilter } from '@/store';
import RangeSlider from '../RangeSlider.vue';

defineProps({
    level: {
        type: String,
        default: 'e',
    },
})

const range=defineModel();

const minbvlim = {
    'b': 1,
    'i': 1,
    'e': 1,
};

const maxbvlim = {
    'b': 54,
    'i': 216,
    'e': 381,
}

const filter=useVideoFilter();

</script>