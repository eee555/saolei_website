<template>
    <!-- @vue-generic {import('@/services/saoleiRankingService').SaoleiRecord} -->
    <ElTableColumn :column-key="field" :prop="field" :label="label" align="right">
        <template #header>
            <button class="stat-header" type="button" :aria-label="`${t(`common.level.${level}`)} ${label}`" :aria-pressed="selected === field" @click="emit('select', field)">
                {{ label }}
            </button>
        </template>
        <template #default="{ row }">
            <PreviewNumber v-if="saoleiVideoId(row, field)" :id="saoleiVideoId(row, field)" :text="formatSaoleiValue(row, field)" />
            <span v-else>{{ formatSaoleiValue(row, field) }}</span>
        </template>
    </ElTableColumn>
</template>

<script setup lang="ts">
import { ElTableColumn } from 'element-plus';
import { computed } from 'vue';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import PreviewNumber from '@/components/PreviewNumber.vue';
import { formatSaoleiValue, SaoleiStat, saoleiVideoId } from '@/services/saoleiRankingService';
import type { SaoleiField, SaoleiLevel } from '@/services/saoleiRankingService';

const props = defineProps({
    level: { type: String as PropType<SaoleiLevel | 'sum'>, required: true },
    stat: { type: String as PropType<SaoleiStat>, required: true },
    selected: { type: String as PropType<SaoleiField>, required: true },
});

const emit = defineEmits<{ select: [field: SaoleiField] }>();

// Element Plus recognizes nested column components by this name.
defineOptions({ name: 'ElTableColumn' });

const { t } = useI18n();
const field = computed<SaoleiField>(() => `${props.level}${props.stat}`);
const label = computed(() => t(`common.prop.${SaoleiStat[props.stat]}`));
</script>

<style scoped>
.stat-header {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.4rem;
    width: 100%;
    border: 0;
    background: transparent;
    color: inherit;
    font: inherit;
    padding: 0;
    cursor: pointer;
}

.stat-header[aria-pressed="true"] {
    color: var(--el-color-primary);
}

.sort-icon {
    flex-shrink: 0;
}
</style>
