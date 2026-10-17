<template>
    <section class="top-summary" data-cy="top-summary" :aria-busy="loading || anchorsLoading">
        <BaseButton class="square-button top-summary-refresh" size="small" :disabled="loading || anchorsLoading" :aria-busy="loading || anchorsLoading || undefined" :aria-label="t('common.action.refresh')" :title="t('common.action.refresh')" data-cy="refresh-top" @click="refresh">
            <BaseIconRefresh :loading="loading || anchorsLoading" aria-hidden="true" />
        </BaseButton>
        <p v-if="failed" role="alert" class="text-danger">
            {{ t('local.recordsFailed') }}
        </p>
        <p v-if="anchorsFailed" role="alert" class="text-danger">
            {{ t('local.anchorsFailed') }}
        </p>
        <p v-if="(loading && !visibleRecords) || (anchorsLoading && !anchors)" role="status">
            {{ t('local.loading') }}
        </p>
        <div v-if="visibleRecords" class="top-radars">
            <section v-for="nf in [false, true]" :key="String(nf)" class="top-panel">
                <TopRadar v-if="anchors" :records="visibleRecords" :anchors="anchors" :nf="nf" />
                <h3 v-else>
                    {{ nf ? 'NF top' : 'top' }}
                </h3>
                <TopRecordTable :records="visibleRecords" :nf="nf" />
            </section>
        </div>
    </section>
</template>

<script setup lang="ts">
import { computed, onScopeDispose, ref, shallowRef, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import TopRadar from './TopRadar.vue';
import TopRecordTable from './TopRecordTable.vue';

import BaseButton from '@/components/common/BaseButton.vue';
import { BaseIconRefresh } from '@/components/common/icon';
import { fetchTopAnchors, fetchTopPlayerRecords } from '@/services/topRankingService';
import type { TopAnchors, TopRecords } from '@/services/topRankingService';

const props = defineProps({
    userId: { type: Number, required: true },
    active: { type: Boolean, default: true },
    revision: { type: String, default: '' },
});
const dataKey = computed(() => `${props.userId}:${props.revision}`);
const loadedKey = ref('');
const records = shallowRef<TopRecords | null>(null);
const anchors = shallowRef<TopAnchors | null>(null);
const visibleRecords = computed(() => (props.active && loadedKey.value === dataKey.value ? records.value : null));
const loading = ref(false);
const failed = ref(false);
const anchorsLoading = ref(false);
const anchorsFailed = ref(false);
let controller: AbortController | null = null;
let anchorsController: AbortController | null = null;
let requestId = 0;
let anchorsRequestId = 0;

async function loadRecords(force = false) {
    controller?.abort();
    const request = ++requestId;
    loading.value = false;
    if (!props.active || props.userId < 1 || (!force && loadedKey.value === dataKey.value)) return;
    controller = new AbortController();
    const { signal } = controller;
    const key = dataKey.value;
    loading.value = true;
    failed.value = false;
    try {
        const result = await fetchTopPlayerRecords(props.userId, signal);
        if (request !== requestId || key !== dataKey.value) return;
        records.value = result;
        loadedKey.value = key;
    } catch {
        if (request === requestId && !signal.aborted) failed.value = true;
    } finally {
        if (request === requestId) loading.value = false;
    }
}

async function loadAnchors(force = false) {
    if (!props.active || props.userId < 1) {
        anchorsRequestId++;
        anchorsController?.abort();
        anchorsLoading.value = false;
        return;
    }
    if (!force && (anchors.value || anchorsLoading.value)) return;
    anchorsController?.abort();
    anchorsController = new AbortController();
    const { signal } = anchorsController;
    const request = ++anchorsRequestId;
    anchorsLoading.value = true;
    anchorsFailed.value = false;
    try {
        const result = await fetchTopAnchors(signal);
        if (request === anchorsRequestId) anchors.value = result;
    } catch {
        if (request === anchorsRequestId && !signal.aborted) anchorsFailed.value = true;
    } finally {
        if (request === anchorsRequestId) anchorsLoading.value = false;
    }
}

function refresh() {
    void loadRecords(true);
    void loadAnchors(true);
}
watch([dataKey, () => props.active], () => {
    void loadRecords();
    void loadAnchors();
}, { immediate: true });
onScopeDispose(() => {
    requestId++;
    anchorsRequestId++;
    controller?.abort();
    anchorsController?.abort();
});

const i18nMessages = {
    'zh-cn': { local: {
        recordsFailed: 'top 成绩加载失败，请刷新重试。',
        anchorsFailed: 'top 锚点加载失败，请刷新重试。',
        loading: '正在加载 top…',
    } },
    en: { local: {
        recordsFailed: 'Could not load top records. Refresh to retry.',
        anchorsFailed: 'Could not load top anchors. Refresh to retry.',
        loading: 'Loading top…',
    } },
};
const { t } = useI18n({ messages: i18nMessages });
</script>

<style scoped>
.top-summary {
    position: relative;
    min-width: 0;
    min-height: 28px;
    margin-bottom: 16px;
}
.top-summary-refresh {
    position: absolute;
    top: 0;
    right: 0;
    z-index: 1;
    width: 28px;
    height: 28px;
}
.top-summary > p {
    padding-right: 36px;
}
.top-radars {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 340px), 1fr));
    gap: 12px;
}
.top-panel {
    min-width: 0;
}
.top-panel h3 {
    text-align: center;
    font-size: var(--ui-font-size-medium);
}
</style>
