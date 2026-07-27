<template>
    <BaseCardNormal>
        <table class="pluck-record-table record-table" cellspacing="0" cellpadding="0">
            <thead>
                <tr>
                    <th class="text text-large" scope="col">
                        {{ t('local.pluckRecord') }}
                    </th>
                    <th class="text text-info" scope="col">
                        {{ t('common.prop.pluck') }}
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="level in DensityCustomLevelConfigs" :key="level.code">
                    <th class="text text-info" scope="row">
                        {{ customLevelLabel(level) }}
                    </th>
                    <td class="text">
                        <PreviewNumber
                            :id="recordByLevel.get(level.code)?.video_id"
                            :text="recordByLevel.get(level.code)?.pluck.toFixed(6)"
                        />
                    </td>
                </tr>
            </tbody>
        </table>
    </BaseCardNormal>
</template>

<script lang="ts" setup>
import type { PropType } from 'vue';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import PreviewNumber from '@/components/PreviewNumber.vue';
import { DensityCustomLevelConfigs } from '@/utils/customlevel';
import type { CustomLevel } from '@/utils/customlevel';

interface PluckRecord {
    level: string;
    video_id: number;
    pluck: number;
}

const props = defineProps({
    records: {
        type: Array as PropType<PluckRecord[]>,
        required: true,
    },
});

const { t } = useI18n({ messages: {
    'zh-cn': { local: {
        pluckRecord: '自定义密度',
    } },
    en: { local: {
        pluckRecord: 'Density',
    } },
} });

const recordByLevel = computed(() => new Map(
    props.records.map((record) => [record.level, record]),
));

function customLevelLabel(customLevel: CustomLevel): string {
    return t('common.level.c', {
        row: customLevel.row,
        column: customLevel.column,
        mine: customLevel.mine,
    });
}
</script>

<style scoped>
.record-table {
    width: 100%;
    table-layout: auto;
}

.record-table th,
.record-table td {
    box-sizing: border-box;
    border-bottom: 1px solid var(--el-table-border-color, var(--el-border-color-lighter));
    padding: 8px 12px;
    text-align: center;
}

.pluck-record-table th,
.pluck-record-table td {
    width: 50%;
}
</style>
