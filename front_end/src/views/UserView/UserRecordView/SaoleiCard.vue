<template>
    <section>
        <h3>{{ t('local.title') }}</h3>
        <ElTable :data="rows" border class="saolei-record-table">
            <ElTableColumn label="Saolei.wang" min-width="130">
                <template #default="{ row }">
                    {{ row.board === 'saolei_nf' ? 'NF' : t('local.all') }}
                </template>
            </ElTableColumn>
            <ElTableColumn v-for="stat in saoleiStats" :key="stat" :label="t(`local.${stat}`)" min-width="115">
                <template #default="{ row }">
                    <PreviewNumber v-if="saoleiVideoId(row.record, stat)" :id="saoleiVideoId(row.record, stat)" :text="formatSaoleiValue(row.record, stat)" />
                    <span v-else>{{ formatSaoleiValue(row.record, stat) }}</span>
                </template>
            </ElTableColumn>
        </ElTable>
    </section>
</template>

<script setup lang="ts">
import { ElTable, ElTableColumn } from 'element-plus';
import { computed } from 'vue';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import PreviewNumber from '@/components/PreviewNumber.vue';
import { formatSaoleiValue, saoleiStats, saoleiVideoId } from '@/services/saoleiRankingService';
import type { SaoleiBoard, SaoleiRecord } from '@/services/saoleiRankingService';

const props = defineProps({
    records: { type: Object as PropType<Partial<Record<SaoleiBoard, SaoleiRecord>>>, required: true },
});
const boards: SaoleiBoard[] = ['saolei', 'saolei_nf'];
const rows = computed(() => boards.map((board) => ({ board, record: props.records[board] })));

const i18nMessages = {
    'zh-cn': { local: {
        title: 'Saolei.wang 纪录',
        all: '标准',
        bt: '初级 Time',
        bb: '初级 3BV/s',
        it: '中级 Time',
        ib: '中级 3BV/s',
        et: '高级 Time',
        eb: '高级 3BV/s',
        sumt: '总 Time',
        sumb: '总 3BV/s',
    } },
    en: { local: {
        title: 'Saolei.wang records',
        all: 'Standard',
        bt: 'Beg Time',
        bb: 'Beg 3BV/s',
        it: 'Int Time',
        ib: 'Int 3BV/s',
        et: 'Exp Time',
        eb: 'Exp 3BV/s',
        sumt: 'Total Time',
        sumb: 'Total 3BV/s',
    } },
};
const { t } = useI18n({ messages: i18nMessages });
</script>

<style scoped>
h3 {
    font-size: 1.1rem;
    margin: 0 0 1rem;
}
</style>
