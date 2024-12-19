<template>
    <div>
        <el-container>
            <el-main style="padding: 1%;">
                <el-tabs type="border-card" style=" min-height: 300px;">
                    <el-tab-pane style="max-height: 300px; overflow: auto;user-select: none;"
                        v-loading="news_queue_status == 1">
                        <template #label>
                            {{ t('home.news') }}&nbsp;
                            <el-text v-if="news_queue_status == 2" type="success"><el-icon>
                                    <Check />
                                </el-icon></el-text>
                            <el-link v-else-if="active_tab == 'newest'" :underline="false"
                                :disabled="news_queue_status != 0" @click="update_news_queue"
                                style="vertical-align: baseline;"><el-icon>
                                    <Refresh />
                                </el-icon></el-link>
                        </template>
                        <div v-for="news in news_queue">
                            <el-text style="margin-right: 5px">
                                {{ utc_to_local_format(news.time) }}
                            </el-text>
                            <PlayerName class="name" style="vertical-align: top;" :user_id="+news.player_id"
                                :user_name="news.player" />
                            <el-text style="vertical-align: middle;">
                                {{ t('news.breakRecordTo', {
                                    mode: t('common.mode.' + news.mode), level:
                                        t('common.level.' + news.level), stat: t('common.prop.' + news.index)
                                }) }}
                            </el-text>
                            <PreviewNumber :id="news.video_id" :text="to_fixed_n(news.value, 3)" />
                            <el-text style="margin-left: 5px; vertical-align: middle;">
                                {{ news.delta == "新" ? "" : news.delta > 0 ? "↑" : "↓" }}{{ news.delta }}
                            </el-text>
                        </div>
                        <!-- 2023年2月26日 11:45 周炎亮 将高级标准模式时间记录刷新为 91.52 ↑3.60-->
                    </el-tab-pane>
                </el-tabs>
                <el-tabs type="border-card" style="margin-top: 2%;" v-model="active_tab">
                    <el-tab-pane class="bottom_tabs" :lazy="true" name="newest" v-loading="newest_queue_status == 1">
                        <template #label>
                            {{ t('home.latestScore') }}&nbsp;
                            <el-text v-if="newest_queue_status == 2" type="success"><el-icon>
                                    <Check />
                                </el-icon></el-text>
                            <el-link v-else-if="active_tab == 'newest'" :underline="false"
                                :disabled="newest_queue_status != 0" @click="update_newest_queue"
                                style="vertical-align: baseline;"><el-icon>
                                    <Refresh />
                                </el-icon></el-link>
                        </template>
                        <VideoList :videos="newest_queue" :reverse="true" upload_time="time" :show-header="false">
                        </VideoList>
                    </el-tab-pane>
                    <el-tab-pane :label="t('home.reviewQueue')" class="bottom_tabs" :lazy="true" name="review">
                        <VideoList :videos="review_queue" :review_mode="store.user.is_staff"
                            @update="update_review_queue" v-loading="review_queue_updating"></VideoList>
                    </el-tab-pane>
                </el-tabs>
            </el-main>
            <el-aside v-if="false" width="30%" style="padding: 1%;">
                <el-tabs v-if="false" type="border-card" style="min-height: 300px;">
                    <el-tab-pane label="每日一星">每日一星</el-tab-pane>
                    <el-tab-pane label="站长统计">站长统计</el-tab-pane>
                    <el-tab-pane label="如何评选？">如何评选？</el-tab-pane>
                </el-tabs>
                <div style="padding-top: 5%;user-select: none;">
                    <div class="aside-tip-title">
                        <el-icon>
                            <Download />
                        </el-icon>下载中心
                    </div>
                    <div style="font-size: 14px;padding: 2% 5%;">
                        <Downloads></Downloads>
                        <span style="width:12px; display:inline-block"></span>
                        <FriendlyLink></FriendlyLink>
                    </div>

                    <div class="aside-tip-title">
                        <el-icon>
                            <QuestionFilled />
                        </el-icon>帮助中心
                    </div>
                    <div style="font-size: 14px;padding: 2% 5%;">
                        <Groups></Groups>
                    </div>

                    <div class="aside-tip-title">
                        <el-icon>
                            <InfoFilled />
                        </el-icon>关于我们
                    </div>
                    <div style="font-size: 14px;padding: 2% 5%;">
                        <Thanks></Thanks>
                        <span style="width:12px; display:inline-block"></span>
                        赞助
                    </div>
                </div>
            </el-aside>
        </el-container>
    </div>
</template>

<script setup lang='ts'>
import { onMounted, ref, Ref } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import PreviewNumber from '@/components/PreviewNumber.vue';
import VideoList from '@/components/VideoList.vue';
import PlayerName from '@/components/PlayerName.vue';
import { to_fixed_n } from "@/utils";
const { proxy } = useCurrentInstance();
import { utc_to_local_format } from "@/utils/system/tools";

import FriendlyLink from "@/components/dialogs/FriendlyLinks.vue";
import Downloads from "@/components/dialogs/Downloads.vue";
import Thanks from "@/components/dialogs/Thanks.vue";
import Groups from "@/components/dialogs/Groups.vue";
import { store } from '../store'

import { useI18n } from 'vue-i18n';
const { t } = useI18n();

const review_queue = ref<any[]>([]);
const newest_queue = ref<any[]>([]);
const news_queue = ref<any[]>([]);
const active_tab = ref('newest');

const review_queue_updating = ref(true);

// 0: 可以刷新, 1: 正在刷新, 2: 刷新完毕，冷却中
const newest_queue_status = ref(1);
const news_queue_status = ref(1);

onMounted(() => {
    update_review_queue()
    update_newest_queue()
    update_news_queue()
})

const update_review_queue = async () => {
    review_queue_updating.value = true;
    await proxy.$axios.get('/video/review_queue/',
        {
            params: {}
        }
    ).then(function (response) {
        review_queue.value.splice(0, review_queue.value.length)
        for (let key in response.data) {
            response.data[key] = JSON.parse(response.data[key] as string);
            response.data[key]["key"] = Number.parseInt(key);
            review_queue.value.push(response.data[key]);
        }
    })
    review_queue_updating.value = false;
}

const update_newest_queue = async () => {
    newest_queue_status.value = 1;
    setTimeout(() => { newest_queue_status.value = 0; }, 5000)
    await proxy.$axios.get('/video/newest_queue/',
        {
            params: {}
        }
    ).then(function (response) {
        for (let key in response.data) {
            response.data[key] = JSON.parse(response.data[key] as string);
            response.data[key]["key"] = Number.parseInt(key);
            newest_queue.value.push(response.data[key]);
            if (response.data[key].state == 'd' && response.data[key].player_id == store.user.id) {
                store.new_identifier = true;
            }
        }
    })
    if (newest_queue_status.value == 1) {
        newest_queue_status.value = 2;
    }
}

const update_news_queue = async () => {
    news_queue_status.value = 1;
    setTimeout(() => { news_queue_status.value = 0; }, 5000)
    await proxy.$axios.get('/video/news_queue/',
        {
            params: {}
        }
    ).then(function (response) {
        news_queue.value = response.data.map((v: string) => { return JSON.parse(v) })
    })
    if (news_queue_status.value == 1) {
        news_queue_status.value = 2;
    }
}

</script>

<style lang='less'>
.bottom_tabs {
    height: 500px;
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
