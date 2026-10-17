<template>
    <ElTabs :model-value="activeTab" @tab-click="handleTabClick">
        <ElTabPane :label="t('local.videos')" name="videos" />
        <ElTabPane :label="t('local.identifiers')" name="identifiers" />
    </ElTabs>
    <router-view v-slot="{ Component }">
        <keep-alive>
            <component :is="Component" />
        </keep-alive>
    </router-view>
</template>

<script setup lang="ts">
import type { TabsPaneContext } from 'element-plus';
import { ElTabPane, ElTabs } from 'element-plus';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const activeTab = computed(() => (route.name === 'database-identifiers' ? 'identifiers' : 'videos'));

function handleTabClick(tab: TabsPaneContext) {
    if (tab.paneName !== undefined) void router.replace({ name: `database-${String(tab.paneName)}` });
}

const i18nMessages = {
    'zh-cn': { local: { videos: '录像', identifiers: '标识查询' } },
    en: { local: { videos: 'Videos', identifiers: 'Identifier Lookup' } },
};
const { t } = useI18n({ messages: i18nMessages });
</script>
