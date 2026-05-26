<template>
    <div ref="containerRef" v-loading="playerLoading" class="personal-homepage" :class="{ 'wide-mode': isWide, 'narrow-mode': !isWide }">
        <div class="profile-section">
            <Profile :user="store.player" :direction="isWide ? 'vertical' : 'horizontal'" />
        </div>
        <div class="content-area">
            <el-tabs :model-value="activeTab" @tab-click="handleTabClick">
                <el-tab-pane v-for="tab in tabItems" :key="tab.name" :label="tab.label" :name="tab.name" />
                <router-view v-slot="{ Component }">
                    <keep-alive>
                        <component :is="Component" v-model:user="store.player" />
                    </keep-alive>
                </router-view>
            </el-tabs>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { useElementSize } from '@vueuse/core';
import { ElTabPane, ElTabs, vLoading } from 'element-plus';
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';

import Profile from './Profile.vue';

import { httpErrorNotification } from '@/components/Notifications';
import { fetchUserInfo } from '@/services/userService';
import { store } from '@/store';
import { UserProfile } from '@/utils/userprofile';

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

const containerRef = ref<HTMLElement | null>(null);
const { width } = useElementSize(containerRef);
const isWide = computed(() => width.value >= 960);

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
        try {
            store.player = new UserProfile(await fetchUserInfo(newId));
        } catch (error) {
            httpErrorNotification(error);
        }
    }
    playerLoading.value = false;
}

watch(() => route.params.id, refresh, { immediate: true });
// onMounted(refresh);

const i18nMessages = {
    'zh-cn': { local: {
        accountlink: '账号关联',
        summary: '概览',
        record: '纪录',
        videos: '录像',
        upload: '上传',
    } },
    'en': { local: {
        accountlink: 'Account Link',
        summary: 'Summary',
        record: 'Record',
        videos: 'Videos',
        upload: 'Upload',
    } },
};

const { t } = useI18n({ messages: i18nMessages });

</script>

<style scoped lang="less">

.personal-homepage {
    display: flex;

    &.narrow-mode {
        flex-direction: column;
        .profile-section { width: 100%; }
        .content-area {
            width: 100%;
            margin-top: 1rem;
        }
    }

    &.wide-mode {
        flex-direction: row;
        .profile-section {
            width: 200px;
            min-width: 200px;
        }
        .content-area {
            flex: 1;
            margin-left: 1rem;
            overflow-y: auto;
        }
    }
}
</style>
