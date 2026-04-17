<template>
    <base-card-normal>
        <div style="margin-bottom: 0.5em;">
            <pr-toolbar>
                <template #start>
                    <span class="text text-medium">
                        {{ t('common.website.saolei') }}&nbsp;#{{ id }}
                    </span>
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
                    <el-descriptions-item :label="t('local.name')" :span="3">
                        {{ info.name }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('local.totalViews')" :span="3">
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
                    <span class="text text-medium">
                        {{ t('accountlink.statSummary') }}
                    </span>
                    &nbsp;
                    <el-button v-loading="taskStatus == 'loading'" @click="updateLink(); $emit('refresh')">
                        {{ t('accountlink.synchronize') }}
                    </el-button>
                </div>
                <div class="text text-small" style="margin-bottom: auto; margin-top: 0.25em;">
                    {{ t('accountlink.statSummaryTooltip') }}
                </div>
                <div style="margin-bottom: 0.25em">
                    <span class="text text-medium">
                        {{ t('accountlink.synchronizeVideos') }}
                    </span>
                    <base-overlay>
                        <base-icon-info />
                        <template #header>
                            扫雷网录像同步功能
                        </template>
                        <template #overlay>
                            <SaoleiImportHelper />
                        </template>
                    </base-overlay>
                </div>
                <div class="text">
                    已收藏{{ importSummary.total }}个录像
                    &nbsp;
                    <span v-if="importSummary.bulk_task_status == 'FAILED'" class="text text-danger">
                        后台任务出错，请联系管理员
                    </span>
                    <span v-else-if="importSummary.bulk_task_status == 'READY'" class="text text-primary">
                        正在排队中
                    </span>
                    <span v-else-if="importSummary.bulk_task_status == 'RUNNING'" class="text text-warning">
                        正在同步中
                    </span>
                    <template v-else>
                        <el-link underline="never" style="vertical-align: top;" @click="syncModeAll = !syncModeAll">
                            {{ syncModeAll ? t('accountlink.synchronizeAll') : t('accountlink.synchronizeNew') }}
                        </el-link>
                        <el-button class="button-compact" @click="syncModeAll ? createSyncTask('all') : createSyncTask('new')">
                            更新
                        </el-button>
                    </template>
                    &nbsp;
                    <el-button v-loading="videoListImporting" class="button-compact" @click="importQueueVisible = true">
                        {{ t('accountlink.synchronizeManage') }}
                    </el-button>
                </div>
                <div class="text" style="margin-top: 0.25em">
                    <StackBar :data="stackBarData" legend />
                </div>
                <div class="text" style="margin-top: 0.5em">
                    新收藏{{ importSummary.new_total }}个录像
                </div>
                <div class="text" style="margin-top: 0.25em">
                    <StackBar :data="stackBarNewData" legend />
                </div>
                <!-- 后端暂时有bug，删不掉 -->
                <!-- <div style="margin-top: auto">
                    <el-button type="danger" plain disabled @click="deleteDialogVisible = true; confirmSaoleiId = ''">
                        {{ t('accountlink.deleteLink') }}
                    </el-button>
                </div> -->
            </el-carousel-item>
        </el-carousel>
        <UnverifiedNotice v-else />

        <el-dialog v-model="importQueueVisible" destroy-on-close style="width: 50em">
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
import 'vue-data-ui/style.css';
import '@/styles/button.css';

import { ElButton, ElCarousel, ElCarouselItem, ElDescriptions, ElDescriptionsItem, ElDialog, ElInput, ElLink, vLoading } from 'element-plus';
import PrToolbar from 'primevue/toolbar';
import { computed, onMounted, PropType, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import CarouselControl from './CarouselControl.vue';
import UnverifiedNotice from './UnverifiedNotice.vue';
import { AccountSaolei, AccountSaoleiDefault, SaoleiImportSummary, SaoleiImportSummaryDefault } from './utils';
import VideoImportQueue from './VideoImportQueue.vue';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import BaseOverlay from '@/components/common/BaseOverlay.vue';
import { BaseIconInfo } from '@/components/common/icon';
import SaoleiImportHelper from '@/components/dialogs/SaoleiImportHelper.vue';
import { httpErrorNotification } from '@/components/Notifications';
import StackBar from '@/components/visualization/StackBar/App.vue';
import { store } from '@/store';
import { cs_to_s, sleep } from '@/utils';
import { TaskStatus } from '@/utils/common/structInterface';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { utc_to_local_format } from '@/utils/system/tools';

const { proxy } = useCurrentInstance();

const refCarousel = ref<typeof ElCarousel>();
const errorMsg = ref('');
const taskStatus = ref<TaskStatus>('');
const deleteDialogVisible = ref(false);
const importQueueVisible = ref(false);
const confirmSaoleiId = ref('');
const syncModeAll = ref(false);
const carouselLength = computed(() => store.player.id == store.user.id ? 2 : 1);

const props = defineProps({
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
    }).then(getImportSummary);
}

const importSummary = ref<SaoleiImportSummary>(SaoleiImportSummaryDefault);
const importSummaryLoading = ref(false);
let importSummarySaoleiId = 0;
const videoImporting = computed(() => importSummary.value.new_connection + importSummary.value.new_failed + importSummary.value.new_success != importSummary.value.new_total);
const videoListImporting = computed(() => ['READY', 'RUNNING'].includes(importSummary.value.bulk_task_status));
const stackBarData = computed(() => [
    { name: t('accountlink.importStatus.successful'), color: '#34d399', value: importSummary.value.old_imported + importSummary.value.new_success },
    { name: t('accountlink.importStatus.running'), color: '#fbbf24', value: importSummary.value.new_total - importSummary.value.new_success - importSummary.value.new_ready - importSummary.value.new_failed - importSummary.value.new_connection },
    { name: t('accountlink.importStatus.ready'), color: '#60a5fa', value: importSummary.value.new_ready },
    { name: t('accountlink.importStatus.connection'), color: '#c084fc', value: importSummary.value.new_connection },
    { name: t('accountlink.importStatus.failed'), color: '#f43f5e', value: importSummary.value.new_failed },
]);
const stackBarNewData = computed(() => [
    { name: t('accountlink.importStatus.successful'), color: '#34d399', value: importSummary.value.new_success },
    { name: t('accountlink.importStatus.running'), color: '#fbbf24', value: importSummary.value.new_total - importSummary.value.new_success - importSummary.value.new_ready - importSummary.value.new_failed - importSummary.value.new_connection },
    { name: t('accountlink.importStatus.ready'), color: '#60a5fa', value: importSummary.value.new_ready },
    { name: t('accountlink.importStatus.connection'), color: '#c084fc', value: importSummary.value.new_connection },
    { name: t('accountlink.importStatus.failed'), color: '#f43f5e', value: importSummary.value.new_failed },
]);

async function getImportSummary() {
    if (props.info.id == 0) return;
    importSummaryLoading.value = true;
    await proxy.$axios.get('/accountlink/saolei/videoimport/stat/', {
        params: {
            saolei_id: props.info.id,
        },
    }).then((response) => {
        importSummary.value = response.data;
    });
    importSummaryLoading.value = false;
}

watch(() => props.info.id, getImportSummary, { immediate: true });

onMounted(async () => {
    while (true) {
        await sleep(30000);
        if (props.info.id != importSummarySaoleiId) {
            importSummarySaoleiId = props.info.id;
        } else if (videoImporting.value || videoListImporting.value) {
            await getImportSummary();
        }
    }
});

defineEmits(['refresh']);

/* 本地化 Localization */
const i18nMessage = {
    'zh-cn': { local: {
        name: '姓名',
        totalViews: '综合人气',
        videoCount: '录像数量',
    } },
    'en': { local: {
        name: 'Name',
        totalViews: 'Total Views',
        videoCount: 'Video Count',
    } },
};

const { t } = useI18n({ messages: i18nMessage });
</script>
