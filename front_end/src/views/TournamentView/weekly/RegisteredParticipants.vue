<template>
    <ElTable v-loading="loading" :data="participants" row-key="id" data-cy="weekly-participants">
        <!-- @vue-generic {TournamentParticipant} -->
        <ElTableColumn :label="t('common.prop.realName')" min-width="150">
            <template #default="{ row }">
                <PlayerName v-if="row.user_id !== 0" :user-id="row.user_id" />
                <span v-else>{{ t('common.anonymous') }}</span>
            </template>
        </ElTableColumn>
        <!-- @vue-generic {TournamentParticipant} -->
        <ElTableColumn :label="t('local.interval')" min-width="330">
            <template #default="{ row }">
                {{ row.start_time ? toISODateTimeString(row.start_time) : '' }} ~ {{ row.end_time ? toISODateTimeString(row.end_time) : '' }}
            </template>
        </ElTableColumn>
        <ElTableColumn prop="token" :label="t('local.token')" min-width="180" />
        <!-- @vue-generic {TournamentParticipant} -->
        <ElTableColumn v-if="canManage" :label="t('common.prop.action')" width="90">
            <template #default="{ row }">
                <ElButton
                    type="danger" plain :aria-label="t('local.deleteParticipant')"
                    :disabled="deleting" data-cy="delete-participant" @click="requestDeletion(row)"
                >
                    <BaseIconDelete />
                </ElButton>
            </template>
        </ElTableColumn>
    </ElTable>
    <ElDialog
        v-if="canManage" v-model="dialogVisible" :title="t('local.deleteParticipant')"
        width="min(460px, 90vw)" :close-on-click-modal="!deleting" :close-on-press-escape="!deleting" :show-close="!deleting"
    >
        <p class="text">
            {{ t('local.confirmDeletion') }}
        </p>
        <template v-if="selectedParticipant">
            <PlayerName v-if="selectedParticipant.user_id !== 0" :user-id="selectedParticipant.user_id" />
            <span v-else>{{ t('common.anonymous') }}</span>
            <div class="text">
                {{ selectedParticipant.token }}
            </div>
        </template>
        <template #footer>
            <ElButton :disabled="deleting" @click="dialogVisible = false">
                {{ t('common.button.cancel') }}
            </ElButton>
            <BaseButtonConfirm :loading="deleting" @click="confirmDeletion" />
        </template>
    </ElDialog>
</template>

<script setup lang="ts">
import { ElButton, ElDialog, ElTable, ElTableColumn, vLoading } from 'element-plus';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseButtonConfirm from '@/components/common/BaseButtonConfirm.vue';
import { BaseIconDelete } from '@/components/common/icon';
import { actionSuccessNotification, httpErrorNotification } from '@/components/Notifications';
import PlayerName from '@/components/PlayerName.vue';
import { deleteParticipant } from '@/services/tournamentService';
import { toISODateTimeString } from '@/utils/datetime';
import type { TournamentParticipant } from '@/utils/tournaments';

const props = defineProps({
    participants: { type: Array<TournamentParticipant>, required: true },
    canManage: { type: Boolean, required: true },
    loading: { type: Boolean, default: false },
});
const emit = defineEmits<{
    deleted: [participantId: number];
}>();
const dialogVisible = ref(false);
const selectedParticipant = ref<TournamentParticipant>();
const deleting = ref(false);

function requestDeletion(participant: TournamentParticipant) {
    selectedParticipant.value = participant;
    dialogVisible.value = true;
}

async function confirmDeletion() {
    if (!props.canManage || !selectedParticipant.value || deleting.value) return;
    const participantId = selectedParticipant.value.id;
    deleting.value = true;
    try {
        await deleteParticipant(participantId);
        emit('deleted', participantId);
        dialogVisible.value = false;
        actionSuccessNotification();
    } catch (error) {
        httpErrorNotification(error);
    } finally {
        deleting.value = false;
    }
}

const i18nMessages = {
    'zh-cn': { local: {
        interval: '参赛时间区间',
        token: '比赛标识',
        deleteParticipant: '删除参赛者',
        confirmDeletion: '确定删除该参赛者吗？',
    } },
    en: { local: {
        interval: 'Session interval',
        token: 'Tournament token',
        deleteParticipant: 'Delete participant',
        confirmDeletion: 'Delete this participant?',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>
