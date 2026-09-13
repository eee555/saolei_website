<template>
    <BaseCardNormal>
        <div class="mineracer-link">
            <PrToolbar>
                <template #start>
                    <span class="text text-medium">
                        {{ t('common.platform.m') }}
                    </span>
                </template>
                <template v-if="session" #end>
                    <ElTag :type="statusTagType">
                        {{ t(`accountlink.mineracer.status.${session.status}`) }}
                    </ElTag>
                </template>
            </PrToolbar>

            <ElSteps :active="activeStep" :finish-status="finishStatus" :process-status="processStatus" align-center>
                <ElStep :title="t('accountlink.mineracer.stepCreate')" />
                <ElStep :title="t('accountlink.mineracer.stepConfirm')" />
                <ElStep :title="t('accountlink.mineracer.stepComplete')" />
            </ElSteps>

            <div class="mineracer-body">
                <ElButton v-if="showStartButton" type="primary" :loading="startLoading" @click="startLink">
                    {{ t(session ? 'accountlink.mineracer.generateNewLink' : 'accountlink.mineracer.generateLink') }}
                </ElButton>

                <template v-if="session">
                    <ElDescriptions border :column="1" size="small">
                        <ElDescriptionsItem :label="t('common.prop.status')">
                            {{ t(`accountlink.mineracer.status.${session.status}`) }}
                        </ElDescriptionsItem>
                        <ElDescriptionsItem v-if="session.status == 'pending'" :label="t('accountlink.mineracer.expiresIn')">
                            {{ remainingTimeText }}
                        </ElDescriptionsItem>
                        <ElDescriptionsItem v-if="session.remote_userid" :label="t('accountlink.mineracer.userId')">
                            {{ session.remote_userid }}
                        </ElDescriptionsItem>
                    </ElDescriptions>

                    <div v-if="session.status == 'pending'" class="mineracer-actions">
                        <ElLink :href="session.verification_uri_complete" target="_blank" rel="noopener noreferrer" type="primary" :underline="false">
                            <BaseIconExternal />
                            {{ t('accountlink.mineracer.openLink') }}
                        </ElLink>
                        <ElButton text :loading="statusLoading" @click="pollSession">
                            <BaseIconRefresh />
                            {{ t('accountlink.mineracer.refreshStatus') }}
                        </ElButton>
                    </div>
                </template>

                <ElAlert v-if="messageKey" :title="t(messageKey)" :type="messageType" show-icon :closable="false" />
            </div>
        </div>
    </BaseCardNormal>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ElAlert, ElButton, ElDescriptions, ElDescriptionsItem, ElLink, ElStep, ElSteps, ElTag } from 'element-plus';
import PrToolbar from 'primevue/toolbar';
import { computed, onBeforeUnmount, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { BaseIconExternal, BaseIconRefresh } from '@/components/common/icon';
import { httpErrorNotification } from '@/components/Notifications';
import { fetchMineracerAccountLinkSession, getMineracerAccountLinkErrorMessageKey, getMineracerAccountLinkHttpErrorCategory, startMineracerAccountLinkSession } from '@/services/accountLinkService';
import type { MineracerAccountLinkSession } from '@/utils/accountlinks';
import { globalNow } from '@/utils/datetime';

const emit = defineEmits<{
    refresh: [];
}>();

const { t } = useI18n();

const MINERACER_FALLBACK_POLL_DELAY_MS = 2500;
const MINERACER_MIN_POLL_DELAY_MS = 500;

const session = ref<MineracerAccountLinkSession>();
const startLoading = ref(false);
const statusLoading = ref(false);
const httpErrorMessageKey = ref('');
let pollTimer: number | undefined;
let refreshedSessionId = '';

const showStartButton = computed(() => session.value === undefined || ['expired', 'failed'].includes(session.value.status));
const activeStep = computed(() => {
    if (session.value === undefined) return 0;
    if (session.value.status === 'confirmed') return 3;
    if (session.value.status === 'pending') return 1;
    return 2;
});
const finishStatus = computed(() => {
    return session.value?.status === 'failed' ? 'error' : 'success';
});
const processStatus = computed(() => {
    return ['expired', 'failed'].includes(session.value?.status ?? '') ? 'error' : 'process';
});
const statusTagType = computed(() => {
    if (session.value?.status === 'confirmed') return 'success';
    if (session.value?.status === 'failed') return 'danger';
    if (session.value?.status === 'expired') return 'info';
    return 'warning';
});
const remainingTimeText = computed(() => formatRemainingTime((session.value?.expires_at.getTime() ?? 0) - globalNow.value.getTime()));
const messageKey = computed(() => {
    if (httpErrorMessageKey.value) return httpErrorMessageKey.value;
    if (session.value?.status === 'failed') return getMineracerAccountLinkErrorMessageKey(session.value.error_category);
    if (session.value?.status === 'expired') return getMineracerAccountLinkErrorMessageKey('expired');
    if (session.value?.status === 'pending' && session.value.error_category) return getMineracerAccountLinkErrorMessageKey(session.value.error_category);
    if (session.value?.status === 'confirmed') return 'accountlink.mineracer.linkSuccess';
    return '';
});
const messageType = computed(() => {
    if (session.value?.status === 'confirmed') return 'success';
    if (session.value?.status === 'pending') return 'warning';
    return 'error';
});

async function startLink() {
    clearPollTimer();
    httpErrorMessageKey.value = '';
    startLoading.value = true;
    try {
        applySession(await startMineracerAccountLinkSession());
    } catch (error) {
        handleHttpError(error);
    } finally {
        startLoading.value = false;
    }
}

async function pollSession() {
    const currentSession = session.value;
    if (currentSession?.status !== 'pending' || statusLoading.value) return;
    clearPollTimer();
    httpErrorMessageKey.value = '';
    statusLoading.value = true;
    try {
        applySession(await fetchMineracerAccountLinkSession(currentSession.session_id));
    } catch (error) {
        handleHttpError(error);
        schedulePoll(MINERACER_FALLBACK_POLL_DELAY_MS);
    } finally {
        statusLoading.value = false;
    }
}

function applySession(nextSession: MineracerAccountLinkSession) {
    session.value = nextSession;
    if (nextSession.status === 'confirmed' && refreshedSessionId !== nextSession.session_id) {
        refreshedSessionId = nextSession.session_id;
        emit('refresh');
    }
    if (nextSession.status === 'pending') {
        schedulePoll();
    } else {
        clearPollTimer();
    }
}

function schedulePoll(delayMs?: number) {
    clearPollTimer();
    const currentSession = session.value;
    if (currentSession?.status !== 'pending') return;
    const nextPollAt = currentSession.next_poll_at?.getTime() ?? Date.now() + MINERACER_FALLBACK_POLL_DELAY_MS;
    const pollAt = Math.min(nextPollAt, currentSession.expires_at.getTime());
    const delay = delayMs ?? Math.max(MINERACER_MIN_POLL_DELAY_MS, pollAt - Date.now());
    pollTimer = window.setTimeout(() => {
        void pollSession();
    }, delay);
}

function clearPollTimer() {
    if (pollTimer === undefined) return;
    window.clearTimeout(pollTimer);
    pollTimer = undefined;
}

function handleHttpError(error: unknown) {
    const category = getMineracerAccountLinkHttpErrorCategory(error);
    if (category === undefined) {
        httpErrorNotification(error);
        return;
    }
    httpErrorMessageKey.value = getMineracerAccountLinkErrorMessageKey(category);
}

function formatRemainingTime(milliseconds: number): string {
    const totalSeconds = Math.max(0, Math.ceil(milliseconds / 1000));
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

onBeforeUnmount(clearPollTimer);
</script>

<style lang="less" scoped>
.mineracer-link {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    min-width: 0;
}

.mineracer-body {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.mineracer-actions {
    align-items: center;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}
</style>
