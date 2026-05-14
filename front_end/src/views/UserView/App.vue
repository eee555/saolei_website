<template>
    <div ref="containerRef" v-loading="playerLoading" class="personal-homepage" :class="{ 'wide-mode': isWide, 'narrow-mode': !isWide }">
        <div v-loading="infoLoading" class="profile-section">
            <Profile :direction="isWide ? 'vertical' : 'horizontal'" />
        </div>
        <div v-loading="videoLoading" class="content-area">
            <el-tabs :model-value="activeTab" @tab-click="handleTabClick">
                <el-tab-pane v-for="tab in tabItems" :key="tab.name" :label="tab.label" :name="tab.name" />
                <router-view v-slot="{ Component }">
                    <keep-alive>
                        <component :is="Component" />
                    </keep-alive>
                </router-view>
            </el-tabs>
        </div>
    </div>
</template>

<script lang="ts" setup>
// 我的地盘页面
import { useElementSize } from '@vueuse/core';
import { ElTabPane, ElTabs, vLoading } from 'element-plus';
import { computed, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';

import Profile from './Profile.vue';

import { httpErrorNotification } from '@/components/Notifications';
import { store } from '@/store';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { UserProfile } from '@/utils/userprofile';
import { VideoAbstract } from '@/utils/videoabstract';

const { proxy } = useCurrentInstance();
const route = useRoute();
const router = useRouter();

const tabItems = computed(() => {
    const ret = [
        { name: 'summary', label: t('local.summary') },
        { name: 'record', label: t('local.record') },
        { name: 'accountlink', label: t('local.accountlink') },
        { name: 'videos', label: t('local.videos') },
    ];
    if (store.isSelf) {
        ret.push({ name: 'upload', label: t('local.upload') });
    }
    return ret;
});
const validTabs = computed(() => tabItems.value.map((item) => item.name));

const activeTab = computed(() => {
    const lastSegment = route.path.split('/').pop();
    return validTabs.value.includes(lastSegment!) ? lastSegment! : 'summary';
});

const handleTabClick = (tab: any) => {
    const tabName = tab.paneName;
    if (tabName) {
        router.replace(`${tabName}`);
    }
};

const playerLoading = ref(false);
const infoLoading = ref(false);
const videoLoading = ref(false);

const containerRef = ref<HTMLElement | null>(null);
const { width } = useElementSize(containerRef);
const isWide = computed(() => width.value >= 768);

async function refresh() {
    const idStr = route.params.id;
    const newId = Number(idStr);
    if (!Number.isInteger(newId) || newId <= 0) {
        console.log(`Invalid user id: ${idStr}`);
        return;
    }
    playerLoading.value = true;
    if (newId === store.user.id) {
        store.player = store.user;
    } else {
        await fetchPlayerInfo(newId);
    }
    if (store.player.videos.length === 0) {
        await fetchPlayerVideos(newId);
    }
    playerLoading.value = false;
}

watch(() => route.params.id, refresh, { immediate: true });
onMounted(refresh);

async function fetchPlayerInfo(playerId: number) {
    await proxy.$axios.get('/api/userprofile/info', {
        params: { user_id: playerId },
    }).then(({ data }) => {
        store.player = UserProfile.from(data);
        playerLoading.value = false;
    }).catch(httpErrorNotification);
    infoLoading.value = false;
}

async function fetchPlayerVideos(playerId: number) {
    videoLoading.value = true;
    await proxy.$axios.get('/api/userprofile/videos', {
        params: { user_id: playerId },
    }).then(({ data }: { data: VideoAbstract[] }) => {
        store.player.videos = data.map((video) => new VideoAbstract(video));
    }).catch(httpErrorNotification);
    videoLoading.value = false;
}

const i18nMessages = {
    'zh-cn': { local: {
        accountlink: '账号关联',
        summary: '概览',
        record: '纪录',
        videos: '录像',
        upload: '上传',
    } },
};

const { t } = useI18n({ messages: i18nMessages });

</script>

<style scoped lang="less">
@breakpoint: 768px;

.personal-homepage {
    display: flex;
    min-height: 100vh;

    .content-area {
        flex: 1;
        padding: 2rem;
        overflow-y: auto;
        border-radius: 1rem;
    }

    &.narrow-mode {
        flex-direction: column;
        .profile-section { width: 100%; }
        .content-area { margin: 1rem; }
    }

    &.wide-mode {
        flex-direction: row;
        .profile-section {
            width: 320px;
            min-width: 280px;
            max-width: 35%;
        }
    }
}
</style>
