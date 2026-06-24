<template>
    <input
        v-bind="inputAttrs"
        :value="displayValue"
        type="number"
        :min="min" :max="max"
        class="base-input-number text text-small"
        :class="externalClass"
        @blur="commitValue" @change="commitValue"
        @input="handleInput" @keydown.enter="commitValue"
    >
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { computed, ref, useAttrs, watch } from 'vue';

import { clamp } from '@/utils/math';

const props = defineProps({
    min: { type: Number, default: -Infinity },
    max: { type: Number, default: Infinity },
});

defineOptions({ inheritAttrs: false });

const model = defineModel<number>({ required: true });

const attrs = useAttrs();
const displayValue = ref(String(model.value));
const externalClass = computed(() => attrs.class);
const inputAttrs = computed(() => {
    const restAttrs = { ...attrs };
    delete restAttrs.class;
    return restAttrs;
});

function parseInput(value: string) {
    if (value.trim() === '') return null;

    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
}

function handleInput(event: Event) {
    const target = event.target as HTMLInputElement;
    const parsed = parseInput(target.value);

    displayValue.value = target.value;
    if (parsed !== null && parsed >= props.min && parsed <= props.max) {
        model.value = parsed;
    }
}

function commitValue() {
    const parsed = parseInput(displayValue.value);
    const nextValue = clamp(parsed ?? model.value, props.min, props.max);

    model.value = nextValue;
    displayValue.value = String(nextValue);
}

watch(model, (value) => {
    displayValue.value = String(clamp(value, props.min, props.max));
});
</script>

<style scoped lang="less">
.base-input-number {
    appearance: textfield;
    box-sizing: border-box;
    height: 24px;
    min-width: 0;
    padding: 1px 8px;
    color: var(--el-input-text-color, var(--el-text-color-regular));
    line-height: 22px;
    background-color: var(--el-input-bg-color, var(--el-fill-color-blank));
    border: 1px solid var(--el-input-border-color, var(--el-border-color));
    border-radius: var(--el-input-border-radius, var(--el-border-radius-base));
    outline: none;
    transition: var(--el-transition-box-shadow), border-color var(--el-transition-duration);

    &::placeholder {
        color: var(--el-input-placeholder-color, var(--el-text-color-placeholder));
    }

    &:hover {
        border-color: var(--el-input-hover-border-color, var(--el-border-color-hover));
    }

    &:focus {
        border-color: var(--el-input-focus-border-color, var(--el-color-primary));
        box-shadow: 0 0 0 1px var(--el-input-focus-border-color, var(--el-color-primary)) inset;
    }

    &:disabled {
        color: var(--el-disabled-text-color);
        cursor: not-allowed;
        background-color: var(--el-disabled-bg-color);
        border-color: var(--el-disabled-border-color);
    }

    &::-webkit-outer-spin-button,
    &::-webkit-inner-spin-button {
        appearance: none;
        margin: 0;
    }
}
</style>
