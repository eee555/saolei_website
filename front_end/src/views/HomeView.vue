<template>
    <div>
        <ElContainer>
            <ElMain style="padding: 1%;">
                <ElTabs type="border-card" style=" min-height: 300px;">
                    <ElTabPane v-loading="news_queue_status == 1" style="max-height: 300px; overflow: auto;user-select: none;">
                        <template #label>
                            {{ t('home.news') }}&nbsp;
                            <span v-if="news_queue_status == 2" class="text text-success">
                                <ElIcon>
                                    <Check />
                                </ElIcon>
                            </span>
                            <ElLink
                                v-else-if="active_tab == 'newest'" underline="never"
                                :disabled="news_queue_status != 0" style="vertical-align: baseline;" @click="update_news_queue"
                            >
                                <BaseIconRefresh />
                            </ElLink>
                        </template>
                        <div v-for="news in news_queue">
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
                            <PreviewNumber :id="news.video_id" :text="to_fixed_n(news.value, 3)" />
                            <span class="text">
                                {{ news.delta == "新" ? "" : Number(news.delta) > 0 ? "↑" : "↓" }}{{ news.delta }}
                            </span>
                        </div>
                    </ElTabPane>
                </ElTabs>
                <ElTabs v-model="active_tab" type="border-card" style="margin-top: 2%;">
                    <ElTabPane v-loading="newest_queue_status == 1" class="bottom_tabs" lazy name="newest">
                        <template #label>
                            {{ t('home.latestScore') }}&nbsp;
                            <span v-if="newest_queue_status == 2" class="text text-success">
                                <ElIcon>
                                    <Check />
                                </ElIcon>
                            </span>
                            <ElLink
                                v-else-if="active_tab == 'newest'" underline="never"
                                :disabled="newest_queue_status != 0" style="vertical-align: baseline;" @click="update_newest_queue"
                            >
                                <BaseIconRefresh />
                            </ElLink>
                        </template>
                        <VideoList :videos="newest_queue" :columns="['state', 'upload_time', 'player', 'software', 'mode', 'level', 'time', 'bv', 'bvs', 'ioe', 'thrp']" sortable paginator />
                    </ElTabPane>
                    <ElTabPane :label="t('home.reviewQueue')" class="bottom_tabs" lazy name="review">
                        <VideoList v-loading="review_queue_updating" :videos="review_queue" :columns="['state', 'upload_time', 'player', 'software', 'mode', 'level', 'time', 'bv', 'bvs', 'ioe', 'thrp']" paginator />
                    </ElTabPane>
                </ElTabs>
            </ElMain>
        </ElContainer>
    </div>
</template>

<script setup lang='ts'>
import '@/styles/text.css';

import { ElContainer, ElIcon, ElLink, ElMain, ElTabPane, ElTabs, vLoading } from 'element-plus';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { BaseIconRefresh } from '@/components/common/icon';
import PlayerName from '@/components/PlayerName.vue';
import PreviewNumber from '@/components/PreviewNumber.vue';
import VideoList from '@/components/VideoList/App.vue';
import { to_fixed_n } from '@/utils';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { utc_to_local_format } from '@/utils/system/tools';
import type { VideoAbstractInfo } from '@/utils/videoabstract';
import { VideoAbstract } from '@/utils/videoabstract';

const { proxy } = useCurrentInstance();
const { t } = useI18n();

interface NewsItem {
    time: string;
    player_id: number;
    video_id: number;
    index: string;
    mode: string;
    level: string;
    value: string;
    delta: string;
}

const review_queue = ref<VideoAbstract[]>([]);
const newest_queue = ref<VideoAbstract[]>([]);
const news_queue = ref<NewsItem[]>([]);
const active_tab = ref('newest');

const review_queue_updating = ref(true);

// 0: 可以刷新, 1: 正在刷新, 2: 刷新完毕，冷却中
const newest_queue_status = ref(1);
const news_queue_status = ref(1);

onMounted(() => {
    void update_review_queue();
    void update_newest_queue();
    void update_news_queue();
});

const update_review_queue = async () => {
    review_queue_updating.value = true;
    await proxy.$axios.get('/api/video/review_queue').then(function ({ data }) {
        review_queue.value = (data as VideoAbstractInfo[]).map((v) => new VideoAbstract(v));
    });
    review_queue_updating.value = false;
};

const update_newest_queue = async () => {
    newest_queue_status.value = 1;
    setTimeout(() => {
        newest_queue_status.value = 0;
    }, 5000);
    await proxy.$axios.get('/video/newest_queue/', {
        params: {},
    }).then(function (response) {
        newest_queue.value.splice(0, newest_queue.value.length);
        for (const key in response.data) {
            const videoid = Number.parseInt(key);
            const videoinfo = JSON.parse(response.data[key] as string);
            newest_queue.value.push(VideoAbstract.fromVideoRedisInfo(videoid, videoinfo));
        }
    });
    if (newest_queue_status.value == 1) {
        newest_queue_status.value = 2;
    }
};

const update_news_queue = async () => {
    news_queue_status.value = 1;
    setTimeout(() => {
        news_queue_status.value = 0;
    }, 5000);
    await proxy.$axios.get('/video/news_queue/', {
        params: {},
    }).then(function ({ data }) {
        news_queue.value = (data as string[]).map((v) => JSON.parse(v) as NewsItem);
    });
    if (news_queue_status.value == 1) {
        news_queue_status.value = 2;
    }
};
</script>

<style lang='less'>
.bottom_tabs {
    overflow: auto;
}

.aside-tip-title {
    font-size: 14px;
    display: flex;
    align-items: center;
    margin-top: 5%;
}

.text-button:hover {
    cursor: pointer;
}
</style>
