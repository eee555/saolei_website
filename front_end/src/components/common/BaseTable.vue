<template>
    <div class="base-table-wrap">
        <table class="base-table" :class="tableClass" :style="tableStyle">
            <caption v-if="$slots.caption">
                <slot name="caption" />
            </caption>
            <colgroup v-if="$slots.columns">
                <slot name="columns" />
            </colgroup>
            <thead v-if="$slots.head">
                <slot name="head" />
            </thead>
            <tbody>
                <tr v-if="empty" class="base-table-empty-row">
                    <td class="base-table-empty" :colspan="columnCount">
                        {{ emptyText }}
                    </td>
                </tr>
                <slot v-else />
            </tbody>
        </table>
    </div>
</template>

<script setup lang="ts">
import '@/styles/table-columns.css';
import '@/styles/table.css';

import type { CSSProperties, PropType } from 'vue';

defineProps({
    empty: { type: Boolean, default: false },
    emptyText: { type: String, default: '' },
    columnCount: { type: Number, default: 1 },
    tableClass: { type: String, default: '' },
    tableStyle: { type: Object as PropType<CSSProperties>, default: () => ({}) },
});

defineSlots<{
    default?: () => unknown;
    head?: () => unknown;
    columns?: () => unknown;
    caption?: () => unknown;
}>();
</script>
