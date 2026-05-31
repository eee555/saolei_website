<template>
    <el-dialog
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
                    <el-select v-model="videoPlayerConfig.backend" style="width: 10rem">
                        <el-option key="flop" value="flop" label="flop-player" />
                        <el-option key="StrangeDust" value="StrangeDust" label="strange-dust.github.io" />
                    </el-select>
                </span>
            </div>
        </template>
        <FlopPlayer v-if="videoPlayerConfig.backend == 'flop'" :src="url" />
        <StrangeDust v-if="videoPlayerConfig.backend == 'StrangeDust'" :src="url" />
    </el-dialog>
</template>

<script setup lang="ts">
import { ElDialog, ElOption, ElSelect } from 'element-plus';
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { httpErrorNotification } from '../Notifications';

import FlopPlayer from './FlopPlayer.vue';
import StrangeDust from './StrangeDust.vue';

import { videoPlayerConfig, videoplayerstore } from '@/store';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { MS_Software } from '@/utils/ms_const';
import { getSoftwareExtension } from '@/utils/strings';

const { proxy } = useCurrentInstance();

const software = ref<MS_Software>('a');
const url = ref('');

watch(videoplayerstore, () => {
    if (videoplayerstore.visible) {
        fetchSoftware(videoplayerstore.id);
        generateURL();
    }
});

async function fetchSoftware(id: number) {
    try {
        const response = await proxy.$axios.get('/video/get_software/',
            { params: { id } },
        );
        software.value = response.data.msg;
    } catch (e) {
        httpErrorNotification(e);
    }
}

function generateURL() {
    url.value = import.meta.env.VITE_BASE_API + '/video/preview/?id=' + videoplayerstore.id + getSoftwareExtension(software.value);
}

const i18nMessages = {
    'zh-cn': { local: {
        video: '录像',
        player: '播放器：',
    } },
    'en': { local: {
        video: 'Video',
        player: 'Video Player: ',
    } },
};

const { t } = useI18n({ messages: i18nMessages });

</script>
