<template>
    <ElTabPane v-loading="loadingStatus == QueueRefreshStatus.Refreshing" style="max-height: 300px; overflow: auto;user-select: none;">
        <template #label>
            {{ t('home.news') }}&nbsp;
            <span v-if="loadingStatus == QueueRefreshStatus.CoolingDown" class="text text-success">
                <ElIcon>
                    <Check />
                </ElIcon>
            </span>
            <ElLink
                v-else underline="never"
                :disabled="loadingStatus != QueueRefreshStatus.Available" style="vertical-align: baseline;" @click="refresh"
            >
                <BaseIconRefresh />
            </ElLink>
        </template>
        <div v-for="news in queue" :key="`${news.time}-${news.video_id}-${news.index}`">
            <span class="text">
                {{ utc_to_local_format(news.time) }}
            </span>
            &nbsp;
            <PlayerName
                class="name" style="vertical-align: top;" :user-id="+news.player_id"
            />
            &nbsp;
            <span class="text">
                {{ t('news.breakRecordTo', {mode: t(`common.mode.${news.mode}`), level: t(`common.level.${news.level}`), stat: t(`common.prop.${news.index}`)}) }}
            </span>
            &nbsp;
            <PreviewNumber :id="news.video_id" :text="formatNewsValue(news)" />
            <span class="text">
                {{ formatNewsDelta(news) }}
            </span>
        </div>
    </ElTabPane>
</template>

<script setup lang='ts'>
import { ElIcon, ElLink, ElTabPane, vLoading } from 'element-plus';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { QueueRefreshStatus } from './utils';

import { BaseIconRefresh } from '@/components/common/icon';
import PlayerName from '@/components/PlayerName.vue';
import PreviewNumber from '@/components/PreviewNumber.vue';
import { ms_to_s, to_fixed_n } from '@/utils';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { utc_to_local_format } from '@/utils/system/tools';

const { proxy } = useCurrentInstance();
const { t } = useI18n();

interface NewsItem {
    time: string;
    player_id: number;
    video_id: number;
    index: string;
    mode: string;
    level: string;
    value: number;
    old_value: number | null;
}

const queue = ref<NewsItem[]>([]);

const loadingStatus = ref(QueueRefreshStatus.Refreshing);

onMounted(refresh);

async function refresh() {
    loadingStatus.value = QueueRefreshStatus.Refreshing;
    setTimeout(() => {
        loadingStatus.value = QueueRefreshStatus.Available;
    }, 5000);
    await proxy.$axios.get('/video/news_queue/', {
        params: {},
    }).then(function ({ data }) {
        queue.value = (data as string[]).map(parseNewsItem).filter((item): item is NewsItem => item !== null);
    });
    if (loadingStatus.value == QueueRefreshStatus.Refreshing) {
        loadingStatus.value = QueueRefreshStatus.CoolingDown;
    }
}

function parseNewsItem(raw: string): NewsItem | null {
    try {
        const item = JSON.parse(raw) as Partial<NewsItem> & { delta?: unknown };
        if (
            typeof item.time !== 'string'
            || typeof item.player_id !== 'number'
            || typeof item.video_id !== 'number'
            || typeof item.index !== 'string'
            || typeof item.mode !== 'string'
            || typeof item.level !== 'string'
            || typeof item.value !== 'number'
            || item.old_value === undefined
            || (item.old_value !== null && typeof item.old_value !== 'number')
            || item.delta !== undefined
        ) {
            return null;
        }
        return item as NewsItem;
    } catch {
        return null;
    }
}

function formatNewsDelta(news: NewsItem): string {
    if (news.old_value === null) {
        return '';
    }
    const delta = news.value - news.old_value;
    const arrow = delta > 0 ? '↑' : '↓';
    return `${arrow}${formatNewsStat(news.index, delta)}`;
}

function formatNewsValue(news: NewsItem): string {
    return formatNewsStat(news.index, news.value);
}

function formatNewsStat(stat: string, value: number): string {
    if (stat === 'timems') {
        return ms_to_s(value);
    }
    return String(to_fixed_n(value, 3));
}
</script>
