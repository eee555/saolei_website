<template>
    <div class="custom-counter-wrap">
        <table class="custom-counter" :style="tableStyle">
            <colgroup>
                <col :style="thColStyle">
                <col :style="tdColStyle">
            </colgroup>
            <tbody>
                <tr v-for="(row, index) in rows" :key="index">
                    <th>{{ row.label }}</th>
                    <td :class="{ 'custom-counter__value--error': row.error }">
                        {{ row.value }}
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script setup lang="ts">
import { Parser } from 'expr-eval';
import type { PropType } from 'vue';
import { computed } from 'vue';

import { videoNumericParamKeys } from './types';
import type { CustomCounterConfig } from './types';

import type { AnyVideo } from '@/utils/fileIO';

const props = defineProps({
    video: { type: Object as PropType<AnyVideo>, required: true },
    currentMs: { type: Number, required: true },
    config: { type: Object as PropType<CustomCounterConfig>, required: true },
});

type DynamicParamValues = Record<string, unknown>;

const allowedKeys = new Set<string>(videoNumericParamKeys);
const parser = new Parser({
    operators: {
        assignment: false,
    },
});

const rows = computed(() => {
    void props.currentMs;
    const values = createEvaluationContext(props.video);
    return props.config.table.map(([label, expression]) => {
        const result = evaluateExpression(expression, values);
        return {
            label,
            ...result,
        };
    });
});

const tableStyle = computed(() => ({
    fontSize: `${Math.max(1, props.config.fontSize)}px`,
    width: `${Math.max(1, props.config.thWidth) + Math.max(1, props.config.tdWidth)}px`,
}));

const thColStyle = computed(() => ({
    width: `${Math.max(1, props.config.thWidth)}px`,
}));

const tdColStyle = computed(() => ({
    width: `${Math.max(1, props.config.tdWidth)}px`,
}));

function evaluateExpression(expression: string, values: DynamicParamValues) {
    try {
        const parsed = parser.parse(expression);
        const unknownVariables = parsed.variables().filter((key) => !allowedKeys.has(key));
        if (unknownVariables.length > 0) throw new Error(`Unknown variable: ${unknownVariables.join(', ')}`);
        return { error: false, value: String(parsed.evaluate(values as Parameters<typeof parsed.evaluate>[0])) };
    } catch (error) {
        return { error: true, value: formatError(error) };
    }
}

function formatError(error: unknown) {
    if (error instanceof Error && error.message !== '') return error.message;
    return String(error);
}

function createEvaluationContext(video: AnyVideo) {
    const values: DynamicParamValues = {};
    for (const key of videoNumericParamKeys) {
        Object.defineProperty(values, key, {
            enumerable: true,
            get: () => video[key],
        });
    }
    return values;
}
</script>

<style scoped>
.custom-counter-wrap {
    max-height: calc(100vh - 290px);
    overflow-y: auto;
}

.custom-counter {
    table-layout: fixed;
    border-collapse: collapse;
    color: var(--el-text-color-regular);
    line-height: 1.25;
}

.custom-counter th,
.custom-counter td {
    box-sizing: border-box;
    border: 1px solid var(--el-border-color);
    padding: 3px 6px;
}

.custom-counter th {
    color: var(--el-text-color-secondary);
    font-weight: 500;
    text-align: left;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.custom-counter td {
    overflow: hidden;
    font-variant-numeric: tabular-nums;
    text-align: right;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.custom-counter__value--error {
    color: var(--el-color-danger);
    overflow-wrap: anywhere;
    text-align: left;
    white-space: normal;
}
</style>
