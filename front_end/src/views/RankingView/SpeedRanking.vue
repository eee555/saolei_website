<template>
    <section class="speed-ranking">
        <div class="ranking-toolbar">
            <ElSelect v-model="selectedBoard" :aria-label="t('local.board')" class="board-selector">
                <ElOption v-for="board in boards" :key="board" :label="t(`local.label.${board}`)" :value="board" :title="t(`local.tooltip.${board}`)" />
            </ElSelect>
            <Tippy>
                <BaseIconInfo />
                <template #content>
                    <ElCard class="card-small">
                        {{ t(`local.tooltip.${selectedBoard}`) }}
                    </ElCard>
                </template>
            </Tippy>
        </div>
        <SaoleiRanking v-if="selectedBoard === 'saolei'" />
    </section>
</template>

<script setup lang="ts">
import '@/styles/cards.css';

import { ElCard, ElOption, ElSelect } from 'element-plus';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Tippy } from 'vue-tippy';

import SaoleiRanking from './SaoleiRanking.vue';

import { BaseIconInfo } from '@/components/common/icon';

const boards = ['saolei'] as const;
const selectedBoard = ref<typeof boards[number]>('saolei');

const i18nMessages = {
    'zh-cn': { local: {
        board: '大榜',
        label: {
            // eslint-disable-next-line @stylistic/quotes
            saolei: "@:{'common.website.saolei'}规则",
        },
        tooltip: {
            // eslint-disable-next-line @stylistic/quotes
            saolei: "仅限@:{'common.mode.std'}@:{'common.prop.mode'}。@:{'common.level.b'}@:{'common.prop.time'}要求@:{'common.prop.bv'} ≥ 2，@:{'common.level.b'}@:{'common.prop.bvs'}要求@:{'common.prop.bv'} ≥ 4，@:{'common.level.i'}要求@:{'common.prop.bv'} ≥ 30，@:{'common.level.e'}要求@:{'common.prop.bv'} ≥ 100",
        },
    } },
    en: { local: {
        board: 'Ranking board',
        label: {
            saolei: '@:common.website.saolei Rule',
        },
        tooltip: {
            // eslint-disable-next-line @stylistic/quotes
            saolei: "@:common.mode.std mode only. @:common.level.b @:common.prop.time requires @:common.prop.bv ≥ 2. @:common.level.b @:common.prop.bvs requires @:common.prop.bv ≥ 4. @:common.level.i requires @:common.prop.bv ≥ 30. @:common.level.e requires @:common.prop.bv ≥ 100.",
        },
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
