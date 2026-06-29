<template>
    <BaseCardNormal>
        <div style="margin-bottom: 0.5em;">
            <PrToolbar>
                <template #start>
                    <span class="text text-medium">
                        {{ t('common.platform.B') }}&nbsp;#{{ id }}
                    </span>
                </template>
                <template #end>
                    <CarouselControl :ref-carousel="refCarousel!" :length="carouselLength" />
                </template>
            </PrToolbar>
        </div>
        <ElCarousel v-if="verified" ref="refCarousel" trigger="click" :autoplay="false" indicator-position="none" :loop="false" arrow="never">
            <ElCarouselItem>
                <ElDescriptions border>
                    <ElDescriptionsItem :label="t('common.prop.update_time')" :span="3">
                        {{ toISODateTimeString(info.update_time) }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('local.name')" :span="3">
                        {{ info.name }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('local.officialTitle')" :span="3">
                        {{ info.official_title }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('local.level')" :span="2">
                        {{ info.level }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('local.videoCount')">
                        {{ info.video_count }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('local.following')" :span="2">
                        {{ info.following }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('local.articleCount')">
                        {{ info.article_count }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('local.follower')" :span="2">
                        {{ info.follower }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('local.opusCount')">
                        {{ info.opus_count }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem v-if="info.sign" :label="t('local.sign')" :span="3">
                        {{ info.sign }}
                    </ElDescriptionsItem>
                </ElDescriptions>
            </ElCarouselItem>
            <ElCarouselItem v-if="store.user.id == store.player.id">
                <div>
                    <span class="text text-large">
                        {{ t('accountlink.statSummary') }}
                    </span>
                    &nbsp;
                    <ElButton @click="updateLink(); $emit('refresh')">
                        {{ t('accountlink.synchronize') }}
                    </ElButton>
                    &nbsp;
                    <IconTaskStatus :status="taskStatus" />
                    <br>
                    <span class="text text-danger text-small">
                        {{ errorMsg }}
                    </span>
                </div>
            </ElCarouselItem>
        </ElCarousel>
        <UnverifiedNotice v-else />
    </BaseCardNormal>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ElButton, ElCarousel, ElCarouselItem, ElDescriptions, ElDescriptionsItem } from 'element-plus';
import PrToolbar from 'primevue/toolbar';
import { computed, ref, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';

import CarouselControl from './CarouselControl.vue';
import UnverifiedNotice from './UnverifiedNotice.vue';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import IconTaskStatus from '@/components/common/IconTaskStatus.vue';
import { httpErrorNotification } from '@/components/Notifications';
import { store } from '@/store';
import { AccountBilibili } from '@/utils/accountlinks';
import type { TaskStatus } from '@/utils/common/structInterface';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { toISODateTimeString } from '@/utils/datetime';

defineProps({
    id: { type: String, default: '0' },
    verified: { type: Boolean, default: false },
    info: { type: AccountBilibili, default: () => new AccountBilibili() },
});

defineEmits(['refresh']);

const { proxy } = useCurrentInstance();

const refCarousel = useTemplateRef<typeof ElCarousel>('refCarousel');
const errorMsg = ref('');
const taskStatus = ref<TaskStatus>('');
const carouselLength = computed(() => (store.player.id == store.user.id ? 2 : 1));

async function updateLink() {
    taskStatus.value = 'loading';
    await proxy.$axios.post('accountlink/update/', {
        platform: 'B',
    }).then(function ({ data }) {
        errorMsg.value = '';
        taskStatus.value = data.type;
        if (data.type == 'error') {
            errorMsg.value = t(`errorMsg.${data.object}.title`) + t('common.punct.colon') + t(`errorMsg.${data.object}.${data.category}`);
        }
    }).catch(function (error: unknown) {
        errorMsg.value = '';
        taskStatus.value = 'error';
        httpErrorNotification(error);
    });
}

const i18nMessage = {
    'zh-cn': { local: {
        articleCount: '专栏',
        follower: '粉丝',
        following: '关注',
        level: '等级',
        name: '昵称',
        officialTitle: '认证',
        opusCount: '动态',
        profile: '资料',
        sign: '签名',
        videoCount: '视频',
    } },
    en: { local: {
        articleCount: 'Articles',
        follower: 'Followers',
        following: 'Following',
        level: 'Level',
        name: 'Name',
        officialTitle: 'Identity',
        opusCount: 'Posts',
        profile: 'Profile',
        sign: 'Signature',
        videoCount: 'Videos',
    } },
};

const { t } = useI18n({ messages: i18nMessage });
</script>

<style lang="less" scoped>
.profile-row {
    align-items: center;
    display: flex;
    min-width: 0;
}

.profile-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
}
</style>
