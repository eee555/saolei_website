<template>
    <ElDialog v-if="progress.total > progress.completed" model-value :title="t('local.title')" width="min(28rem, 90vw)" :show-close="false" :close-on-click-modal="false" :close-on-press-escape="false" append-to-body>
        <div aria-busy="true" aria-live="polite">
            <p class="text-regular">
                {{ t('local.progress', progress) }}
            </p>
            <ElProgress :percentage="Math.floor(progress.completed / progress.total * 100)" />
        </div>
    </ElDialog>
</template>

<script setup lang="ts">
import { ElDialog, ElProgress } from 'element-plus';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';

import { videoInfoDownloads } from '@/services/videoInfoService';

const route = useRoute();
const progress = computed(() => {
    const items = new Map<string, boolean>();
    for (const task of videoInfoDownloads.value) {
        if (task.page !== route.fullPath.split('#')[0]) continue;
        for (const [key, done] of task.items) items.set(key, (items.get(key) ?? true) && done);
    }
    return { total: items.size, completed: [...items.values()].filter(Boolean).length };
});

const i18nMessages = {
    'zh-cn': { local: {
        title: '正在获取录像信息',
        progress: '已获取 {completed} / {total}，请稍候。',
    } },
    en: { local: {
        title: 'Loading video information',
        progress: '{completed} / {total} loaded. Please wait.',
    } },
};
const { t } = useI18n({ messages: i18nMessages });
</script>
