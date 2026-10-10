<template>
    <div class="checkbox-buttons" role="group" :aria-label="t('common.prop.state')">
        <label v-for="item of statelist" :key="item.state" class="checkbox-button">
            <input v-model="checkboxGroup" class="checkbox-button-input" type="checkbox" :value="item.state" @change="handleChange">
            <span class="checkbox-button-content">{{ t(`common.state.${item.state}`) }}</span>
        </label>
    </div>
</template>

<script setup lang="ts">
import { nextTick } from 'vue';
import { useI18n } from 'vue-i18n';

const emit = defineEmits<{ change: [value: string[]] }>();
const checkboxGroup = defineModel({ type: Array<string>, required: true });
const statelist = [
    { state: 'c' },
    { state: 'd' },
    { state: 'a' },
    { state: 'b' },
];

const { t } = useI18n();

async function handleChange() {
    // Parent v-model props must update before reading the new selection.
    await nextTick();
    emit('change', checkboxGroup.value);
}
</script>
