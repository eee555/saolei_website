<template>
    <span class="text">
        <ElLink :href="gscGuideUrl" target="_blank" rel="noopener noreferrer">
            {{ t('gsc.identifierGuide.guideLink') }}
        </ElLink>
        <template v-if="token === ''">
            <br>
            {{ t('gsc.identifierGuide.preparing') }}
        </template>
        <template v-else-if="!participant">
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
            <template v-if="identifier === ''">
                <ElInput v-model="newIdentifier" :placeholder="t('common.prop.identifier')" style="width: 260px" />
                <ElButton :loading="registeringIdentifier" @click="registerIdentifier">
                    {{ t('common.button.register') }}
                </ElButton>
                <span v-if="errorText !== ''" class="text text-danger">
                    {{ errorText }}
                </span>
            </template>
            <template v-else>
                {{ t('gsc.identifierGuide.identifier') }}
                <span class="ttfamily">{{ identifier }}</span>
                <IconCopy :text="identifier" />
            </template>
        </template>
    </span>
</template>

<script setup lang="ts">
import { ElButton, ElInput, ElLink } from 'element-plus';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import '@/styles/text.css';
import { httpErrorNotification, successNotification, unknownErrorNotification } from '@/components/Notifications';
import IconCopy from '@/components/widgets/IconCopy.vue';
import { local } from '@/store';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const props = defineProps({
    order: {
        type: Number,
        default: 0,
    },
    token: {
        type: String,
        default: '',
    },
});
const emit = defineEmits<{
    (event: 'refresh'): void;
}>();

const identifier = defineModel('identifier', {
    type: String,
    default: '',
});
const participant = defineModel('participant', {
    type: Boolean,
    default: false,
});

const { proxy } = useCurrentInstance();
const { t } = useI18n();

const errorText = ref<string>('');
const newIdentifier = ref<string>('');
const registeringParticipant = ref(false);
const registeringIdentifier = ref(false);

const gscGuideUrl = computed(() => {
    const base = typeof import.meta.env.VITE_DOCS_URL === 'string' && import.meta.env.VITE_DOCS_URL.length > 0
        ? import.meta.env.VITE_DOCS_URL
        : import.meta.env.DEV ? 'http://localhost:5173/docs/' : '/docs/';
    const normalizedBase = base.endsWith('/') ? base : `${base}/`;
    const path = local.value.language.startsWith('en') ? 'en/guide/gsc' : 'guide/gsc';
    return `${normalizedBase}${path}`;
});

async function registerParticipant() {
    registeringParticipant.value = true;
    await proxy.$axios.post('/api/tournament/gsc/participant', {
        order: props.order,
    }).then((response) => {
        successNotification(response);
        participant.value = true;
        emit('refresh');
    }).catch(httpErrorNotification);
    registeringParticipant.value = false;
}

async function registerIdentifier() {
    registeringIdentifier.value = true;
    await proxy.$axios.post('/api/tournament/gsc/participant/identifier', {
        identifier: newIdentifier.value,
        order: props.order,
    }).then((response) => {
        const { data } = response;
        switch (data.type) {
            case 'success':
                successNotification(response);
                identifier.value = newIdentifier.value;
                newIdentifier.value = '';
                emit('refresh');
                break;
            case 'error':
                switch (data.category) {
                    case 'suffix': errorText.value = t('msg.identifierIncorrectSuffix'); break;
                    case 'collision': errorText.value = t('msg.identifierOccupied'); break;
                    case 'invalid': errorText.value = t('msg.identifierIllegal'); break;
                    default: unknownErrorNotification(response);
                }
                break;
            default:
                unknownErrorNotification(response);
        }
    }).catch(httpErrorNotification);
    registeringIdentifier.value = false;
}
</script>

<style scoped>
.ttfamily {
    font-family: 'Courier New', Courier, monospace;
}
</style>
