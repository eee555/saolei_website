<template>
    <BaseTable v-loading="loading" class="pb-ranking-table" :empty="rows.length === 0" :column-count="3 + pbStats.length" :empty-text="t('ranking.empty')">
        <template #head>
            <tr>
                <th scope="col" class="rank-cell">
                    #
                </th>
                <th scope="col" class="player-cell">
                    {{ t('common.prop.player') }}
                </th>
                <th v-for="stat in pbStats" :key="stat" scope="col" class="stat-cell">
                    {{ t(`common.prop.${stat}`) }}
                </th>
                <th scope="col" class="upload-cell">
                    {{ t('common.prop.upload_time') }}
                </th>
            </tr>
        </template>
        <tr
            v-for="(row, index) in rows" :key="row.player_id" class="pb-ranking-row" :tabindex="loading ? -1 : 0"
            @click="previewVideo(row)" @keydown.enter.self.prevent="!loading && previewVideo(row)" @keydown.space.self.prevent="!loading && previewVideo(row)"
        >
            <td class="rank-cell">
                {{ first + index + 1 }}
            </td>
            <td class="player-cell">
                <PlayerName :user-id="row.player_id" />
            </td>
            <td v-for="stat in pbStats" :key="stat" class="stat-cell">
                {{ formatPBValue(row.timems, level, bv, stat) }}
            </td>
            <td class="upload-cell">
                {{ formatPBUploadTime(row.upload_time) }}
            </td>
        </tr>
    </BaseTable>
</template>

<script setup lang="ts">
import { vLoading } from 'element-plus';
import type { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseTable from '@/components/common/BaseTable.vue';
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
.pb-ranking-row {
    cursor: pointer;
}

.pb-ranking-row:focus-visible {
    outline: 2px solid var(--ui-color-primary);
    outline-offset: -2px;
}

.rank-cell {
    width: 60px;
    min-width: 60px;
    text-align: center;
}

.player-cell {
    min-width: 150px;
}

.stat-cell {
    min-width: 100px;
    text-align: right;
    white-space: nowrap;
}

.upload-cell {
    min-width: 170px;
    text-align: center;
    white-space: nowrap;
}
</style>
