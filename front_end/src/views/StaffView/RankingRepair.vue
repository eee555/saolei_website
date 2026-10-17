<template>
    <form class="ranking-repair" @submit.prevent="rebuild">
        <label>
            {{ t('local.ranking') }}
            <ElSelect v-model="rankingName" :aria-label="t('local.ranking')" :disabled="working">
                <ElOption :label="t('local.standard')" value="saolei" />
                <ElOption :label="t('local.nf')" value="saolei_nf" />
            </ElSelect>
        </label>
        <label>
            {{ t('local.stat') }}
            <ElSelect v-model="stat" :aria-label="t('local.stat')" :disabled="working">
                <ElOption v-for="field in saoleiFields" :key="field" :label="t(`local.${field}`)" :value="field" />
            </ElSelect>
        </label>
        <label>
            {{ t('common.prop.userId') }}
            <ElInputNumber v-model="userId" :aria-label="t('common.prop.userId')" :min="1" :precision="0" :controls="false" :disabled="working" />
        </label>
        <BaseButton native-type="submit" :disabled="!canRebuild" :loading="working">
            <template #icon>
                <i class="pi pi-refresh" aria-hidden="true" />
            </template>
            {{ t('local.rebuild') }}
        </BaseButton>
    </form>
    <output v-if="result" class="text" aria-live="polite">
        {{ t('local.completed', { stat: t(`local.${stat}`), value: formatSaoleiValue(result, stat) }) }}
        <span v-if="saoleiVideoId(result, stat)">{{ t('local.videoId', { id: saoleiVideoId(result, stat) }) }}</span>
    </output>
</template>

<script setup lang="ts">
import { ElInputNumber, ElOption, ElSelect } from 'element-plus';
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseButton from '@/components/common/BaseButton.vue';
import { actionSuccessNotification, httpErrorNotification } from '@/components/Notifications';
import type { SaoleiField, SaoleiRankingName, SaoleiRecord } from '@/services/saoleiRankingService';
import { formatSaoleiValue, rebuildSaoleiRecord, saoleiFields, saoleiVideoId } from '@/services/saoleiRankingService';
import '@/styles/text.css';

const rankingName = ref<SaoleiRankingName>('saolei');
const stat = ref<SaoleiField>('bt');
const userId = ref<number>();
const working = ref(false);
const result = ref<SaoleiRecord>();
const canRebuild = computed(() => userId.value !== undefined && Number.isSafeInteger(userId.value) && userId.value > 0);

watch([rankingName, stat, userId], () => {
    result.value = undefined;
});

async function rebuild() {
    if (!canRebuild.value || working.value || userId.value === undefined) return;
    working.value = true;
    result.value = undefined;
    try {
        result.value = await rebuildSaoleiRecord(userId.value, rankingName.value, stat.value);
        actionSuccessNotification();
    } catch (error) {
        httpErrorNotification(error);
    } finally {
        working.value = false;
    }
}

const i18nMessages = {
    'zh-cn': { local: {
        ranking: '大榜',
        stat: '小榜',
        standard: '扫雷网规则（普通）',
        nf: '扫雷网规则（NF）',
        rebuild: '重建纪录',
        completed: '重建完成：{stat} {value}',
        videoId: '，录像 ID {id}',
        bt: '初级 Time',
        bb: '初级 3BV/s',
        it: '中级 Time',
        ib: '中级 3BV/s',
        et: '高级 Time',
        eb: '高级 3BV/s',
        sumt: 'Time 总和',
        sumb: '3BV/s 总和',
    } },
    en: { local: {
        ranking: 'Ranking',
        stat: 'Statistic',
        standard: 'Saolei.wang rules (Standard)',
        nf: 'Saolei.wang rules (NF)',
        rebuild: 'Rebuild record',
        completed: 'Rebuild complete: {stat} {value}',
        videoId: ', video ID {id}',
        bt: 'Beginner Time',
        bb: 'Beginner 3BV/s',
        it: 'Intermediate Time',
        ib: 'Intermediate 3BV/s',
        et: 'Expert Time',
        eb: 'Expert 3BV/s',
        sumt: 'Time Sum',
        sumb: '3BV/s Sum',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>

<style scoped>
.ranking-repair {
    display: flex;
    align-items: end;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 8px;
}

label {
    display: grid;
    gap: 4px;
    width: 220px;
    max-width: 100%;
}
</style>
