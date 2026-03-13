<template>
    <base-card-normal>
        <div style="margin-bottom: 0.5em;">
            <pr-toolbar>
                <template #start>
                    <el-text size="large">
                        {{ t('common.website.saolei') }}&nbsp;#{{ id }}
                    </el-text>
                </template>
                <template #end>
                    <CarouselControl :ref-carousel="refCarousel" :length="carouselLength" />
                </template>
            </pr-toolbar>
        </div>
        <el-carousel v-if="verified" ref="refCarousel" trigger="click" :autoplay="false" indicator-position="none" :loop="false" arrow="never">
            <el-carousel-item>
                <el-descriptions border>
                    <el-descriptions-item :label="t('common.prop.update_time')" :span="3">
                        {{ utc_to_local_format(info.update_time!) }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('accountlink.saoleiName')" :span="3">
                        {{ info.name }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('accountlink.saoleiTotalViews')" :span="3">
                        {{ info.total_views }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.level.b')" :span="3">
                        {{ cs_to_s(info.b_t_ms! / 10) }}
                        &nbsp;|&nbsp;
                        {{ cs_to_s(info.b_b_cent!) }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.level.i')" :span="3">
                        {{ cs_to_s(info.i_t_ms! / 10) }}
                        &nbsp;|&nbsp;
                        {{ cs_to_s(info.i_b_cent!) }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.level.e')" :span="3">
                        {{ cs_to_s(info.e_t_ms! / 10) }}
                        &nbsp;|&nbsp;
                        {{ cs_to_s(info.e_b_cent!) }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.level.sum')">
                        {{ cs_to_s((info.b_t_ms! + info.i_t_ms! + info.e_t_ms!) / 10) }}
                        &nbsp;|&nbsp;
                        {{ cs_to_s(info.b_b_cent! + info.i_b_cent! + info.e_b_cent!) }}
                    </el-descriptions-item>
                </el-descriptions>
            </el-carousel-item>
            <el-carousel-item style="display: flex; flex-direction: column;">
                <div>
                    <el-text size="large">
                        {{ t('accountlink.statSummary') }}
                    </el-text>
                    &nbsp;
                    <el-button @click="updateLink(); $emit('refresh')">
                        {{ t('accountlink.synchronize') }}
                    </el-button>
                </div>
                <el-text tag="div" size="small" style="margin-bottom: auto; margin-top: 0.25em;">
                    {{ t('accountlink.statSummaryTooltip') }}
                </el-text>
                <div>
                    <el-text size="large">
                        {{ t('accountlink.synchronizeVideos') }}
                    </el-text>
                </div>
                <div style="margin-top: 0.25em;">
                    <el-button @click="createSyncTask('new')">
                        {{ t('accountlink.synchronizeNew') }}
                    </el-button>
                    <el-button @click="createSyncTask('all')">
                        {{ t('accountlink.synchronizeAll') }}
                    </el-button>
                    <el-button @click="importQueueVisible = true">
                        {{ t('accountlink.synchronizeManage') }}
                    </el-button>
                </div>
                <el-text tag="div" size="small" style="margin-top: 0.25em;">
                    {{ t('accountlink.synchronizeTooltip') }}
                </el-text>
                <!-- 后端暂时有bug，删不掉 -->
                <!-- <div style="margin-top: auto">
                    <el-button type="danger" plain disabled @click="deleteDialogVisible = true; confirmSaoleiId = ''">
                        {{ t('accountlink.deleteLink') }}
                    </el-button>
                </div> -->
            </el-carousel-item>
        </el-carousel>
        <UnverifiedNotice v-else />

        <el-dialog v-model="importQueueVisible" destroy-on-close>
            <VideoImportQueue :saolei-id="info.id" />
        </el-dialog>
    </base-card-normal>

    <el-dialog v-model="deleteDialogVisible" title="请输入扫雷网ID" style="width: 15em">
        <el-input v-model="confirmSaoleiId" style="width: 7.8em" />
        &nbsp;
        <el-button :disabled="confirmSaoleiId != info.id.toString()" type="danger" plain @click="deleteAccountLink">
            确认解除
        </el-button>
    </el-dialog>
</template>

<script setup lang="ts">
import { ElButton, ElCarousel, ElCarouselItem, ElDescriptions, ElDescriptionsItem, ElDialog, ElInput, ElText } from 'element-plus';
import PrToolbar from 'primevue/toolbar';
import { computed, PropType, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import CarouselControl from './CarouselControl.vue';
import UnverifiedNotice from './UnverifiedNotice.vue';
import { AccountSaolei, AccountSaoleiDefault } from './utils';
import VideoImportQueue from './VideoImportQueue.vue';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { httpErrorNotification } from '@/components/Notifications';
import { store } from '@/store';
import { cs_to_s } from '@/utils';
import { TaskStatus } from '@/utils/common/structInterface';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { utc_to_local_format } from '@/utils/system/tools';

const { t } = useI18n();
const { proxy } = useCurrentInstance();

const refCarousel = ref<typeof ElCarousel>();
const errorMsg = ref('');
const taskStatus = ref<TaskStatus>('');
const deleteDialogVisible = ref(false);
const importQueueVisible = ref(false);
const confirmSaoleiId = ref('');
const carouselLength = computed(() => store.player.id == store.user.id ? 2 : 1);

defineProps({
    id: { type: String, default: '0' },
    verified: { type: Boolean, default: false },
    info: { type: Object as PropType<AccountSaolei>, default: () => AccountSaoleiDefault },
});

async function updateLink() {
    taskStatus.value = 'loading';
    await proxy.$axios.post('accountlink/update/', {
        platform: 'c',
    }).then(function (response) {
        const data = response.data;
        errorMsg.value = '';
        taskStatus.value = data.type;
        if (data.type == 'error') {
            errorMsg.value = t(`errorMsg.${data.object}.title`) + t('common.punct.colon') + t(`errorMsg.${data.object}.${data.category}`);
        }
    }).catch(function (error) {
        errorMsg.value = '';
        taskStatus.value = 'error';
        httpErrorNotification(error);
    });
}

function deleteAccountLink() {
    proxy.$axios.post('/accountlink/delete/', {
        platform: 'c',
    }).then().catch(httpErrorNotification);
    deleteDialogVisible.value = false;
}

function createSyncTask(mode: 'all' | 'new') {
    proxy.$axios.post('/accountlink/saolei_import_videos/', {
        mode: mode,
    });
}

defineEmits(['refresh']);
</script>
