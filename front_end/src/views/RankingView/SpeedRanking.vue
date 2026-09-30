<template>
    <section class="speed-ranking">
        <div class="ranking-toolbar">
            <ElSelect v-model="selectedBoard" :aria-label="t('local.board')" class="board-selector">
                <ElOption v-for="board in boards" :key="board.id" :label="board.label" :value="board.id" />
            </ElSelect>
        </div>
        <SaoleiRanking v-if="selectedBoard === 'saolei'" />
    </section>
</template>

<script setup lang="ts">
import { ElOption, ElSelect } from 'element-plus';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

import SaoleiRanking from './SaoleiRanking.vue';

const boards = [{ id: 'saolei', label: 'Saolei.wang' }] as const;
const selectedBoard = ref<typeof boards[number]['id']>('saolei');

const i18nMessages = {
    'zh-cn': { local: {
        board: '大榜',
    } },
    en: { local: {
        board: 'Ranking board',
    } },
};
const { t } = useI18n({ messages: i18nMessages });
</script>

<style scoped>
.speed-ranking {
    min-width: 0;
}

.ranking-toolbar {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-bottom: 1rem;
}

.board-selector {
    width: 12rem;
    max-width: 100%;
}
</style>
