<template>
    <span class="text">
        <ElLink :href="weeklyGuideUrl" target="_blank" rel="noopener noreferrer">
            {{ t('gsc.identifierGuide.guideLink') }}
        </ElLink>
        <template v-if="token === '' && !registrationOpen">
            <br>
            {{ t('gsc.identifierGuide.preparing') }}
        </template>
        <template v-else-if="token === ''">
            <br>
            <ElButton :loading="registeringParticipant" @click="registerParticipant">
                {{ t('common.button.register') }}
            </ElButton>
        </template>
        <template v-else>
            <br>
            {{ t('gsc.identifierGuide.token') }}
            <span class="ttfamily">{{ token }}</span>
            <IconCopy :text="token" />
            <br>
            <span data-cy="weekly-participant-window">
                有效时间{{ t('common.punct.colon') }}
                {{ displayTime(participant?.start_time) }}
                &nbsp;~&nbsp;
                {{ displayTime(participant?.end_time) }}
            </span>
        </template>
    </span>
</template>

<script setup lang="ts">
import { ElButton, ElLink } from 'element-plus';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import '@/styles/text.css';
import { httpErrorNotification, successNotification } from '@/components/Notifications';
import IconCopy from '@/components/widgets/IconCopy.vue';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { toDate, toISODateTimeString } from '@/utils/datetime';
import type { TournamentParticipant } from '@/utils/tournaments';

const props = defineProps({
    tournamentId: {
        type: Number,
        required: true,
    },
    registrationOpen: {
        type: Boolean,
        default: false,
    },
    participant: {
        type: Object as () => TournamentParticipant | null,
        default: null,
    },
});
const emit = defineEmits<{
    (event: 'refresh'): void;
}>();

const token = defineModel('token', {
    type: String,
    default: '',
});

const { proxy } = useCurrentInstance();
const { t } = useI18n();

const registeringParticipant = ref(false);

const weeklyGuideUrl = computed(() => {
    const base = typeof import.meta.env.VITE_DOCS_URL === 'string' && import.meta.env.VITE_DOCS_URL.length > 0
        ? import.meta.env.VITE_DOCS_URL
        : import.meta.env.DEV ? 'http://localhost:5173/docs/' : '/docs/';
    const normalizedBase = base.endsWith('/') ? base : `${base}/`;
    const path = 'guide/weekly-tournament';
    return `${normalizedBase}${path}`;
});

async function registerParticipant() {
    registeringParticipant.value = true;
    await proxy.$axios.post('/api/tournament/weekly/participant', {
        id: props.tournamentId,
    }).then((response) => {
        successNotification(response);
        token.value = response.data.token;
        emit('refresh');
    }).catch(httpErrorNotification);
    registeringParticipant.value = false;
}

function displayTime(time: string | Date | null | undefined) {
    const date = toDate(time);
    return date ? toISODateTimeString(date) : '';
}
</script>

<style scoped>
.ttfamily {
    font-family: 'Courier New', Courier, monospace;
}
</style>
