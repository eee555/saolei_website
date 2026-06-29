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
                {{ toISODateTimeString(info.update_time) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem :label="t('accountlink.msgamesName')" :span="3">
                {{ info.name }}
            </ElDescriptionsItem>
            <ElDescriptionsItem :label="t('accountlink.msgamesLocalName')" :span="3">
                {{ info.local_name }}
            </ElDescriptionsItem>
            <ElDescriptionsItem :label="t('accountlink.msgamesJoined')" :span="3">
                {{ toISODateTimeString(info.joined) }}
            </ElDescriptionsItem>
        </ElDescriptions>
        <UnverifiedNotice v-else />
    </BaseCardNormal>
</template>

<script setup lang="ts">
import { ElDescriptions, ElDescriptionsItem } from 'element-plus';
import PrToolbar from 'primevue/toolbar';
import { useI18n } from 'vue-i18n';

import UnverifiedNotice from './UnverifiedNotice.vue';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { AccountMSGames } from '@/utils/accountlinks';
import { toISODateTimeString } from '@/utils/datetime';

defineProps({
    id: { type: String, default: '' },
    verified: { type: Boolean, default: false },
    info: { type: AccountMSGames, default: () => new AccountMSGames() },
});

const { t } = useI18n();
</script>
