<template>
    <BaseCardNormal>
        <div style="margin-bottom: 0.5em;">
            <PrToolbar>
                <template #start>
                    <span class="text text-medium">
                        Authoritative Minesweeper&nbsp;#{{ id }}
                    </span>
                </template>
            </PrToolbar>
        </div>
        <ElDescriptions v-if="verified" border>
            <ElDescriptionsItem :label="t('common.prop.update_time')" :span="3">
                {{ utc_to_local_format(info.update_time) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem :label="t('accountlink.msgamesName')" :span="3">
                {{ info.name }}
            </ElDescriptionsItem>
            <ElDescriptionsItem :label="t('accountlink.msgamesLocalName')" :span="3">
                {{ info.local_name }}
            </ElDescriptionsItem>
            <ElDescriptionsItem :label="t('accountlink.msgamesJoined')" :span="3">
                {{ info.joined }}
            </ElDescriptionsItem>
        </ElDescriptions>
        <UnverifiedNotice v-else />
    </BaseCardNormal>
</template>

<script setup lang="ts">
import { ElDescriptions, ElDescriptionsItem } from 'element-plus';
import PrToolbar from 'primevue/toolbar';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import UnverifiedNotice from './UnverifiedNotice.vue';
import { AccountMSGames, AccountMSGamesDefault } from './utils';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { utc_to_local_format } from '@/utils/system/tools';

defineProps({
    id: { type: String, default: '' },
    verified: { type: Boolean, default: false },
    info: {
        type: Object as PropType<AccountMSGames>,
        default: () => AccountMSGamesDefault,
    },
});

const { t } = useI18n();
</script>
