<template>
    <ElTable v-loading="loading" :data="rows" row-key="player_id" border class="pb-ranking-table" :empty-text="t('local.empty')">
        <ElTableColumn type="index" label="#" :index="(index) => first + index + 1" width="60" align="center" />
        <!-- @vue-generic {PBRankingPlayer} -->
        <ElTableColumn column-key="player" :label="t('common.prop.player')" min-width="150">
            <template #default="{ row }">
                <PlayerName :user-id="row.player_id" />
            </template>
        </ElTableColumn>
        <!-- @vue-generic {PBRankingPlayer} -->
        <ElTableColumn v-for="stat in pbStats" :key="stat" :column-key="stat" :label="t(`common.prop.${stat}`)" min-width="100" align="right">
            <template #default="{ row }">
                <PreviewNumber v-if="stat === 'time'" :id="row.video_id" :text="formatPBValue(row.timems, level, bv, stat)" />
                <span v-else>{{ formatPBValue(row.timems, level, bv, stat) }}</span>
            </template>
        </ElTableColumn>
        <!-- @vue-generic {PBRankingPlayer} -->
        <ElTableColumn prop="upload_time" :label="t('common.prop.upload_time')" min-width="170" align="center">
            <template #default="{ row }">
                {{ formatPBUploadTime(row.upload_time) }}
            </template>
        </ElTableColumn>
    </ElTable>
</template>

<script setup lang="ts">
import { ElTable, ElTableColumn, vLoading } from 'element-plus';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import PlayerName from '@/components/PlayerName.vue';
import PreviewNumber from '@/components/PreviewNumber.vue';
import { formatPBUploadTime, formatPBValue, pbStats } from '@/services/pbRankingService';
import type { PBRankingPlayer } from '@/services/pbRankingService';
import type { MS_Level } from '@/utils/ms_const';

defineProps({
    rows: { type: Array as PropType<PBRankingPlayer[]>, required: true },
    level: { type: String as PropType<MS_Level>, required: true },
    bv: { type: Number, required: true },
    first: { type: Number, required: true },
    loading: { type: Boolean, required: true },
});

const i18nMessages = {
    'zh-cn': { local: { empty: '暂无纪录' } },
    en: { local: { empty: 'No records' } },
};
const { t } = useI18n({ messages: i18nMessages });
</script>
