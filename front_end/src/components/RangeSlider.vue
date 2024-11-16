<template>
    <div class="slider-demo-block">
        <div>
            <el-slider range :min="props.min" :max="props.max" v-model="range" @change="$emit('change', range)"></el-slider>
        </div>
        <div>
            <!-- @vue-expect-error -->
            <el-input-number size="small" :step-strictly="true" v-model="range[0]" :min="props.min" :max="range[1]"
                :value-on-clear="props.min" @change="$emit('change', range)">
            </el-input-number>
            {{ text }}
            <!-- @vue-expect-error -->
            <el-input-number size="small" :step-strictly="true" v-model="range[1]" :min="range[0]" :max="props.max"
                :value-on-clear="props.max" @change="$emit('change', range)">
            </el-input-number>
        </div>
    </div>
</template>

<script setup lang="ts" name="RangeSlider">

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

const range = defineModel();

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
