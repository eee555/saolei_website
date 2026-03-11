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
                    <CarouselControl :ref-carousel="refCarousel" :length="2" />
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
            <el-carousel-item>
                <div>
                    <el-text size="large">
                        统计数据
                    </el-text>
                    &nbsp;
                    <el-button>更新</el-button>
                </div>
                <el-text tag="div" size="small" style="margin-bottom: 2em; margin-top: 0.25em;">
                    统计数据仅包括纪录、人气、录像数量
                </el-text>
                <div>
                    <el-text size="large">
                        同步录像
                    </el-text>
                    &nbsp;
                    <el-button @click="createSyncTask('new')">
                        增量
                    </el-button>
                    <el-button @click="createSyncTask('all')">
                        全量
                    </el-button>
                </div>
                <el-text tag="div" size="small" style="margin-bottom: 2em; margin-top: 0.25em;">
                    同步录像会创建一个后台任务，代替您从扫雷网下载录像并上传到开源扫雷网。它会访问您的扫雷网个人地盘，逐页扫描所有录像，然后依次下载录像。增量同步扫描到没有新录像的一页即停止，消耗资源较少。全量同步会扫描每一页，消耗资源较多。
                </el-text>
                <div style="margin-top: 3em">
                    <!-- 后端暂时有bug，删不掉 -->
                    <el-button type="danger" plain disabled @click="deleteDialogVisible = true; confirmSaoleiId = ''">
                        解除账号关联
                    </el-button>
                </div>
            </el-carousel-item>
        </el-carousel>
        <el-result v-else icon="warning" title="账号未验证" sub-title="请联系管理员" />
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
import { ElButton, ElCarousel, ElCarouselItem, ElDescriptions, ElDescriptionsItem, ElDialog, ElInput, ElLink, ElResult, ElText } from 'element-plus';
import PrToolbar from 'primevue/toolbar';
import { PropType, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import CarouselControl from './CarouselControl.vue';
import { AccountSaolei, AccountSaoleiDefault } from './utils';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { BaseIconNext, BaseIconPrev } from '@/components/common/icon';
import { httpErrorNotification } from '@/components/Notifications';
import { cs_to_s } from '@/utils';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { utc_to_local_format } from '@/utils/system/tools';

const { t } = useI18n();
const { proxy } = useCurrentInstance();

const refCarousel = ref<typeof ElCarousel>();
const deleteDialogVisible = ref(false);
const confirmSaoleiId = ref('');

defineProps({
    id: { type: String, default: '0' },
    verified: { type: Boolean, default: false },
    info: { type: Object as PropType<AccountSaolei>, default: () => AccountSaoleiDefault },
});

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

</script>
