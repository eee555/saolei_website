<template>
    <base-card-normal>
        <div style="margin-bottom: 0.5em;">
            <pr-toolbar>
                <template #start>
                    <span class="text text-medium">
                        Authoritative Minesweeper&nbsp;#{{ id }}
                    </span>
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
        <UnverifiedNotice v-else />
    </base-card-normal>
</template>

<script setup lang="ts">
import { ElDescriptions, ElDescriptionsItem, ElText } from 'element-plus';
import PrToolbar from 'primevue/toolbar';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import UnverifiedNotice from './UnverifiedNotice.vue';
import { AccountMSGames, AccountMSGamesDefault } from './utils';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { utc_to_local_format } from '@/utils/system/tools';

const { t } = useI18n();

defineProps({
    id: { type: String, default: '' },
    verified: { type: Boolean, default: false },
    info: {
        type: Object as PropType<AccountMSGames>,
        default: () => AccountMSGamesDefault,
    },
});
</script>
