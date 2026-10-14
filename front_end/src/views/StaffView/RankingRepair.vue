<template>
    <form class="ranking-repair" @submit.prevent="rebuild">
        <label>
            大榜
            <ElSelect v-model="rankingName" aria-label="大榜" :disabled="working">
                <ElOption label="扫雷网规则（普通）" value="saolei" />
                <ElOption label="扫雷网规则（NF）" value="saolei_nf" />
            </ElSelect>
        </label>
        <label>
            小榜
            <ElSelect v-model="stat" aria-label="小榜" :disabled="working">
                <ElOption v-for="field in saoleiFields" :key="field" :label="statLabels[field]" :value="field" />
            </ElSelect>
        </label>
        <label>
            用户 ID
            <ElInputNumber v-model="userId" aria-label="用户 ID" :min="1" :precision="0" :controls="false" :disabled="working" />
        </label>
        <BaseButton native-type="submit" :disabled="!canRebuild" :loading="working">
            <template #icon>
                <i class="pi pi-refresh" aria-hidden="true" />
            </template>
            重建纪录
        </BaseButton>
    </form>
    <output v-if="result" class="text" aria-live="polite">
        重建完成：{{ statLabels[stat] }} {{ formatSaoleiValue(result, stat) }}
        <span v-if="saoleiVideoId(result, stat)">，录像 ID {{ saoleiVideoId(result, stat) }}</span>
    </output>
</template>

<script setup lang="ts">
import { ElInputNumber, ElOption, ElSelect } from 'element-plus';
import { computed, ref, watch } from 'vue';

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
const statLabels: Record<SaoleiField, string> = {
    bt: '初级 Time',
    bb: '初级 3BV/s',
    it: '中级 Time',
    ib: '中级 3BV/s',
    et: '高级 Time',
    eb: '高级 3BV/s',
    sumt: 'Time 总和',
    sumb: '3BV/s 总和',
};

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
