<template>
    <base-card-normal class="card">
        <div style="margin-bottom: 0.5em;">
            <pr-toolbar>
                <template #start>
                    <el-text size="large">
                        Authoritative Minesweeper&nbsp;#{{ info.id }}
                    </el-text>
                </template>
            </pr-toolbar>
        </div>
        <el-descriptions v-if="verified" border>
            <el-descriptions-item :label="t('common.prop.update_time')" :span="3">
                {{ utc_to_local_format(info.update_time) }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('accountlink.msgamesName')" :span="3">
                {{ info.name }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('accountlink.msgamesLocalName')" :span="3">
                {{ info.local_name }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('accountlink.msgamesJoined')" :span="3">
                {{ info.joined }}
            </el-descriptions-item>
        </el-descriptions>
        <el-result v-else icon="warning" title="账号未验证" sub-title="请联系管理员" />
    </base-card-normal>
</template>

<script setup lang="ts">
import { ElDescriptions, ElDescriptionsItem, ElResult, ElText } from 'element-plus';
import PrToolbar from 'primevue/toolbar';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import { AccountMSGames, AccountMSGamesDefault } from './utils';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { utc_to_local_format } from '@/utils/system/tools';

import './style.css';

const { t } = useI18n();

defineProps({
    verified: { type: Boolean, default: false },
    info: {
        type: Object as PropType<AccountMSGames>,
        default: () => AccountMSGamesDefault,
    },
});
</script>
