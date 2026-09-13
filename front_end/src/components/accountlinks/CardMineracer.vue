<template>
    <BaseCardNormal>
        <div style="margin-bottom: 0.5em;">
            <PrToolbar>
                <template #start>
                    <span class="text text-medium">
                        {{ t('common.platform.m') }}&nbsp;#{{ id }}
                    </span>
                </template>
            </PrToolbar>
        </div>
        <ElDescriptions v-if="verified" border>
            <ElDescriptionsItem :label="t('accountlink.mineracer.userId')" :span="3">
                {{ info.id }}
            </ElDescriptionsItem>
            <ElDescriptionsItem :label="t('common.prop.status')" :span="3">
                {{ t('accountlink.verified') }}
            </ElDescriptionsItem>
            <ElDescriptionsItem :label="t('common.prop.update_time')" :span="3">
                {{ toISODateTimeString(info.update_time) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem :label="t('local.website')" :span="3">
                <ElLink :href="platformlist[AccountLinkPlatform.Mineracer].profile(id)" target="_blank" rel="noopener noreferrer" type="primary">
                    <BaseIconExternal />
                    {{ t('common.platform.m') }}
                </ElLink>
            </ElDescriptionsItem>
        </ElDescriptions>
        <UnverifiedNotice v-else />
    </BaseCardNormal>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ElDescriptions, ElDescriptionsItem, ElLink } from 'element-plus';
import PrToolbar from 'primevue/toolbar';
import { useI18n } from 'vue-i18n';

import UnverifiedNotice from './UnverifiedNotice.vue';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { BaseIconExternal } from '@/components/common/icon';
import { AccountLinkPlatform, AccountMineracer, platformlist } from '@/utils/accountlinks';
import { toISODateTimeString } from '@/utils/datetime';

defineProps({
    id: { type: String, default: '' },
    verified: { type: Boolean, default: false },
    info: { type: AccountMineracer, default: () => new AccountMineracer() },
});

const i18nMessage = {
    'zh-cn': { local: {
        website: '网站',
    } },
    en: { local: {
        website: 'Website',
    } },
};

const { t } = useI18n({ messages: i18nMessage });
</script>
