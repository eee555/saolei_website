<template>
    <section class="speed-ranking">
        <div class="ranking-toolbar">
            <ElSelect v-model="selectedRankingName" :aria-label="t('local.rankingName')" class="ranking-selector">
                <ElOption v-for="rankingName in rankingNames" :key="rankingName" :label="t(`local.label.${rankingName}`)" :value="rankingName" :title="t(`local.tooltip.${rankingName}`)" />
            </ElSelect>
            <Tippy>
                <BaseIconInfo />
                <template #content>
                    <ElCard class="card-small">
                        {{ t(`local.tooltip.${selectedRankingName}`) }}
                    </ElCard>
                </template>
            </Tippy>
        </div>
        <SaoleiRanking v-if="selectedRankingName === 'saolei'" />
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

const rankingNames = ['saolei'] as const;
const selectedRankingName = ref<typeof rankingNames[number]>('saolei');

const i18nMessages = {
    'zh-cn': { local: {
        rankingName: '大榜',
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
        rankingName: 'Ranking',
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

.ranking-selector {
    width: 12rem;
    max-width: 100%;
}
</style>
