<template>
    <div class="slider-demo-block">
        <div>
            <el-slider v-model="range" range :min="props.min" :max="props.max" @change="$emit('change', range)" />
        </div>
        <div>
            <!-- @vue-expect-error -->
            <el-input-number 
                v-model="range[0]" size="small" :step-strictly="true" :min="props.min" :max="range[1]"
                :value-on-clear="props.min" @change="$emit('change', range)"
            />
            {{ text }}
            <!-- @vue-expect-error -->
            <el-input-number 
                v-model="range[1]" size="small" :step-strictly="true" :min="range[0]" :max="props.max"
                :value-on-clear="props.max" @change="$emit('change', range)"
            />
        </div>
    </div>
</template>

<script setup lang="ts" name="RangeSlider">

import { ElSlider, ElInputNumber } from 'element-plus';

const props = defineProps({
    min: {
        type: Number,
        default: 0,
    },
    max: {
        type: Number,
        default: 100,
    },
    text: {
        type: String,
        default: "",
    },
});

const range = defineModel({ type: Array, required: true });

defineEmits(['change']);
</script>

<style scoped>
.slider-demo-block {
    width: 200px;
    align-content: center;
    display: inline-block;
}

.el-slider {
    height: 20px;
}

.el-input-number {
    margin: 0px;
    width: 90px;
    height: 20px;
}

.el-input-number:nth-child(1) {
    float: left;
}

.el-input-number:nth-child(2) {
    float: right;
}
</style>
