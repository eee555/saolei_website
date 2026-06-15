<template>
    <div v-if="!videoPlayerConfig.strangeDustTrust">
        <ElResult icon="warning">
            <template #title>
                {{ t('local.playerTooltip1') }}
                <PlayerName :user-id="114" />
                {{ t('local.playerTooltip2') }}
            </template>
            <template #sub-title>
                <ElLink href="https://strange-dust.github.io/minesweeper-replay-analyzer/" target="_blank" rel="noopener noreferrer">
                    https://strange-dust.github.io/minesweeper-replay-analyzer/
                </ElLink>
            </template>
            <template #extra>
                <ElButton size="large" @click="videoPlayerConfig.strangeDustTrust = true">
                    {{ t('local.ITrustIt') }}
                </ElButton>
            </template>
        </ElResult>
    </div>
    <iframe v-else :src="`https://strange-dust.github.io/minesweeper-replay-analyzer/?replay=${src}`" style="width: calc(95vw - 50px); height: calc(100vh - 200px); background-color: transparent" />
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ElButton, ElLink, ElResult } from 'element-plus';
import { useI18n } from 'vue-i18n';

import PlayerName from '@/components/PlayerName.vue';
import { videoPlayerConfig } from '@/store';

defineProps({
    src: { type: String, default: '' },
});

const i18nMessages = {
    'zh-cn': { local: {
        ITrustIt: '我信任该网站',
        playerTooltip1: '此播放器来自',
        playerTooltip2: '制作的第三方网站',
    } },
    'en': { local: {
        ITrustIt: 'I trust the website',
        playerTooltip1: 'This video player originated from a third-party website created by ',
        playerTooltip2: ',',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>
