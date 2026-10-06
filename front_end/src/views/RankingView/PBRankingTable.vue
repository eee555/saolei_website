<template>
    <ElTable v-loading="loading" :data="rows" row-key="player_id" border class="pb-ranking-table" :empty-text="t('ranking.empty')" @row-click="previewVideo">
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
                {{ formatPBValue(row.timems, level, bv, stat) }}
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
import { formatPBUploadTime, formatPBValue, pbStats } from '@/services/pbRankingService';
import type { PBRankingPlayer } from '@/services/pbRankingService';
import { preview } from '@/utils/common/PlayerDialog';
import type { MS_Level } from '@/utils/ms_const';

defineProps({
    rows: { type: Array as PropType<PBRankingPlayer[]>, required: true },
    level: { type: String as PropType<MS_Level>, required: true },
    bv: { type: Number, required: true },
    first: { type: Number, required: true },
    loading: { type: Boolean, required: true },
});

function previewVideo(row: PBRankingPlayer) {
    void preview(row.video_id);
}

const { t } = useI18n();
</script>

<style scoped>
:deep(.el-table__row) {
    cursor: pointer;
}
</style>
