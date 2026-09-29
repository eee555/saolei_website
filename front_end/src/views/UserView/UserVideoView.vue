<template>
    <ElRow>
        <UserArbiterCSV :id="user.id" />
        <span style="flex: 1" />
        <ElButton circle :type="showSetting ? 'primary' : 'default'" @click="showSetting = !showSetting">
            <BaseIconSetting />
        </ElButton>
    </ElRow>
    <MultiSelector v-if="showSetting" v-model="VideoListConfig.profile" :options="thisColumnChoices" :labels="thisColumnChoices.map((s) => t(`common.prop.${s}`))" />
    <VideoList
        v-if="loadedUserId === user.id && user.videos !== undefined"
        v-loading="loading" :videos="user.videos" :columns="VideoListConfig.profile" sortable paginator
    >
        <template v-if="isOwnProfile" #rowActions="{ video, close }">
            <ElButton text :disabled="!video.ongoing_tournament || revealing" data-cy="reveal-video" @click="requestReveal(video.id); close()">
                <BaseIconShow />&nbsp;{{ t('local.reveal') }}
            </ElButton>
        </template>
    </VideoList>
    <ElDialog
        v-if="isOwnProfile" v-model="dialogVisible" :title="t('local.reveal')" append-to-body width="min(460px, 90vw)"
        :close-on-click-modal="!revealing" :close-on-press-escape="!revealing" :show-close="!revealing"
    >
        <p>{{ t('local.confirmReveal') }}</p>
        <template #footer>
            <ElButton :disabled="revealing" @click="dialogVisible = false">
                {{ t('common.button.cancel') }}
            </ElButton>
            <BaseButtonConfirm :loading="revealing" @click="confirmReveal" />
        </template>
    </ElDialog>
</template>

<script lang="ts" setup>
// 个人主页的个人所有录像部分
import { ElButton, ElDialog, ElRow, vLoading } from 'element-plus';
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseButtonConfirm from '@/components/common/BaseButtonConfirm.vue';
import { BaseIconSetting, BaseIconShow } from '@/components/common/icon';
import { actionSuccessNotification, httpErrorNotification } from '@/components/Notifications';
import VideoList from '@/components/VideoList/App.vue';
import MultiSelector from '@/components/widgets/MultiSelector.vue';
import UserArbiterCSV from '@/components/widgets/UserArbiterCSV.vue';
import { fetchUserVideos, revealUserVideo } from '@/services/userService';
import { store, VideoListConfig } from '@/store';
import { ArrayUtils } from '@/utils/arrays';
import { LoginStatus } from '@/utils/common/structInterface';
import { ColumnChoices } from '@/utils/ms_const';
import { UserProfile } from '@/utils/userprofile';

const user = defineModel('user', { type: UserProfile, required: true });

const showSetting = ref(false);
const thisColumnChoices = ArrayUtils.sortByReferenceOrder(['bv', 'bvs', 'stnb', 'ces', 'cls', 'corr', 'end_time', 'ioe', 'level', 'state', 'software', 'thrp', 'time', 'upload_time', 'path', 'pluck', 'file_size', 'mode'], ColumnChoices);

const loading = ref(false);
const loadedUserId = ref(0);
const isOwnProfile = computed(() => store.login_status === LoginStatus.IsLogin && store.user.id === user.value.id);
const dialogVisible = ref(false);
const selectedVideoId = ref<number>();
const revealing = ref(false);

function requestReveal(videoId: number) {
    selectedVideoId.value = videoId;
    dialogVisible.value = true;
}

async function confirmReveal() {
    if (!isOwnProfile.value || revealing.value || selectedVideoId.value === undefined) return;
    const videoId = selectedVideoId.value;
    const owner = user.value;
    revealing.value = true;
    try {
        await revealUserVideo(videoId);
        const video = owner.videos?.find((item) => item.id === videoId);
        if (video) video.ongoing_tournament = false;
        dialogVisible.value = false;
        actionSuccessNotification();
    } catch (error) {
        httpErrorNotification(error);
    } finally {
        revealing.value = false;
    }
}

watch(() => user.value.id, () => {
    dialogVisible.value = false;
    selectedVideoId.value = undefined;
});

async function refresh() {
    if (loading.value) return;
    if (user.value.id < 1) return;
    const userId = user.value.id;
    loadedUserId.value = 0;
    loading.value = true;
    try {
        const videos = await fetchUserVideos(userId);
        if (user.value.id === userId) {
            user.value.videos = videos;
            loadedUserId.value = userId;
        }
    } finally {
        loading.value = false;
    }
}

watch(user, refresh, { immediate: true });

const i18nMessages = {
    'zh-cn': { local: {
        reveal: '公开录像',
        confirmReveal: '公开后所有人都能观看此录像，且无法重新隐藏。录像仍计入其参加的所有比赛。确定公开吗？',
    } },
    en: { local: {
        reveal: 'Reveal video',
        confirmReveal: 'Everyone will be able to watch this video, and it cannot be hidden again. It will still count in all its tournaments. Reveal it?',
    } },
};
const { t } = useI18n({ messages: i18nMessages });
</script>
