<template>
    <ElDialog
        v-model="videoplayerstore.visible" style="backdrop-filter: blur(1px); height: fit-content;" align-center destroy-on-close
        :modal="false" :lock-scroll="false" width="fit-content"
    >
        <template #header>
            <div style="display: flex">
                <span>
                    {{ t('local.video') }} #{{ videoplayerstore.id }}
                </span>
                <span style="margin-left: auto;">
                    {{ t('local.player') }}
                    <ElSelect v-model="videoPlayerConfig.backend" style="width: 10rem">
                        <ElOption key="native" value="native" :label="t('local.native')" />
                        <ElOption key="flop" value="flop" label="flop-player" />
                        <ElOption key="StrangeDust" value="StrangeDust" label="strange-dust.github.io" />
                    </ElSelect>
                </span>
            </div>
        </template>
        <FlopPlayer v-if="videoPlayerConfig.backend == 'flop'" :src="videoplayerstore.url" />
        <NativePlayer v-if="videoPlayerConfig.backend == 'native'" :src="videoplayerstore.url" />
        <StrangeDust v-if="videoPlayerConfig.backend == 'StrangeDust'" :src="videoplayerstore.url" />
    </ElDialog>
</template>

<script setup lang="ts">
import { ElDialog, ElOption, ElSelect } from 'element-plus';
import { useI18n } from 'vue-i18n';

import FlopPlayer from './FlopPlayer.vue';
import NativePlayer from './NativePlayer.vue';
import StrangeDust from './StrangeDust.vue';

import { videoPlayerConfig, videoplayerstore } from '@/store';

const i18nMessages = {
    'zh-cn': { local: {
        video: '录像',
        player: '播放器：',
        native: '原生',
    } },
    en: { local: {
        video: 'Video',
        player: 'Video Player: ',
        native: 'Native',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>
