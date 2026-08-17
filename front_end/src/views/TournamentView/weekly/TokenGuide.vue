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
import { local } from '@/store';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const props = defineProps({
    tournamentId: {
        type: Number,
        required: true,
    },
    registrationOpen: {
        type: Boolean,
        default: false,
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
    const path = local.value.language.startsWith('en') ? 'en/guide/tournament' : 'guide/tournament';
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
</script>

<style scoped>
.ttfamily {
    font-family: 'Courier New', Courier, monospace;
}
</style>
