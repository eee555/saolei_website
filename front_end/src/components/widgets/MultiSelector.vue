<template>
    <div class="checkbox-group">
        <label v-for="(option, i) in options" :key="`check-${option}`" class="checkbox checkbox--small">
            <input v-model="selected" class="checkbox-input" type="checkbox" :value="option">
            <span>{{ _labels[i] }}</span>
        </label>
    </div>
    <ElTag v-for="(option) in selected" :key="`tag-${option}`" closable size="small" round @close="handleClose(option)">
        {{ _labels[options.indexOf(option)] }}
    </ElTag>
</template>

<script setup lang="ts">
import { ElTag } from 'element-plus';
import type { PropType } from 'vue';
import { computed } from 'vue';

const props = defineProps({
    options: {
        type: Array as PropType<readonly string[] | string[]>,
        required: true,
    },
    labels: {
        type: Array as PropType<readonly string[] | string[]>,
        default: undefined,
    },
});

const selected = defineModel<string[]>({
    type: Array as PropType<string[]>,
    default: () => [],
});

const _labels = computed(() => props.labels ?? props.options);

function handleClose(tag: string) {
    selected.value.splice(selected.value.indexOf(tag), 1);
}
</script>
