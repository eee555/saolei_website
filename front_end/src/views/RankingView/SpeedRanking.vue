<template>
    <section class="speed-ranking">
        <div class="ranking-toolbar">
            <ElSelect v-model="selectedRankingName" :aria-label="t('local.rankingName')" class="ranking-selector">
                <ElOption v-for="rankingName in rankingNames" :key="rankingName" :label="t(`local.label.${rankingName}`)" :value="rankingName" :title="t(`local.tooltip.${rankingName}`)" />
            </ElSelect>
            <Tippy>
                <BaseIconInfo />
                <template #content>
                    <div class="card card-small">
                        {{ t(`local.tooltip.${selectedRankingName}`) }}
                    </div>
                </template>
            </Tippy>
        </div>
        <RouterView />
    </section>
</template>

<script setup lang="ts">
import '@/styles/cards.css';

import { ElOption, ElSelect } from 'element-plus';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterView, useRoute, useRouter } from 'vue-router';
import { Tippy } from 'vue-tippy';

import { BaseIconInfo } from '@/components/common/icon';

const rankingNames = ['top', 'saolei', 'pb'] as const;
const route = useRoute();
const router = useRouter();
const selectedRankingName = computed<typeof rankingNames[number]>({
    get: () => rankingNames.find((name) => route.name === `ranking_speed_${name}`) ?? 'top',
    set: (name) => {
        void router.push({ name: `ranking_speed_${name}` });
    },
});

const i18nMessages = {
    'zh-cn': { local: {
        rankingName: '大榜',
        label: {
            top: 'Top',
            pb: 'PB 榜',
            saolei: '@:{\'common.website.saolei\'}规则',
        },
        tooltip: {
            top: '标准模式、已审核且非隐藏比赛录像，取每项最佳五条的均值。初级 3BV ≥ 10，中级 ≥ 30，高级 ≥ 100；缺项用时按 999.999 秒补齐，其他指标补 0。',
            pb: '仅限@:{\'common.mode.std\'}@:{\'common.prop.mode\'}，按@:{\'common.prop.level\'}和@:{\'common.prop.bv\'}分榜',
            saolei: '仅限@:{\'common.mode.std\'}@:{\'common.prop.mode\'}。@:{\'common.level.b\'}@:{\'common.prop.time\'}要求@:{\'common.prop.bv\'} ≥ 2，@:{\'common.level.b\'}@:{\'common.prop.bvs\'}要求@:{\'common.prop.bv\'} ≥ 4，@:{\'common.level.i\'}要求@:{\'common.prop.bv\'} ≥ 30，@:{\'common.level.e\'}要求@:{\'common.prop.bv\'} ≥ 100',
        },
    } },
    en: { local: {
        rankingName: 'Ranking',
        label: {
            top: 'Top',
            pb: 'PB',
            saolei: '@:common.website.saolei Rule',
        },
        tooltip: {
            top: 'Mean of the best five official, public Standard replays. Minimum 3BV: Beginner 10, Intermediate 30, Expert 100. Missing times count as 999.999 seconds; other missing values count as zero.',
            pb: 'Standard mode, grouped by level and 3BV. NF additionally requires zero effective right clicks.',
            saolei: '@:common.mode.std mode only. @:common.level.b @:common.prop.time requires @:common.prop.bv ≥ 2. @:common.level.b @:common.prop.bvs requires @:common.prop.bv ≥ 4. @:common.level.i requires @:common.prop.bv ≥ 30. @:common.level.e requires @:common.prop.bv ≥ 100.',
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
