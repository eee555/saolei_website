<template>
    <div>
        <span class="text text-medium">
            {{ t('local.description') }}
        </span>
        <ElRow style="height: 1em" />
        <ElDescriptions border style="max-width: 600px">
            <ElDescriptionsItem :label="t('software.operatingSystem')" :span="2">
                Windows
            </ElDescriptionsItem>
            <ElDescriptionsItem :label="t('software.supportedLanguages')">
                <BaseFlagUK />&nbsp;<BaseFlagCN />&nbsp;<BaseFlagJP />
            </ElDescriptionsItem>
            <ElDescriptionsItem :label="t('software.feature')" :span="3">
                <BaseTagSupport>
                    {{ t('software.features.customMode') }}
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport>
                    {{ t('software.features.customCounter') }}
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport :support="false">
                    {{ t('software.features.noGuessing') }}
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport :support="false">
                    {{ t('software.features.cellScale') }}
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport :support="false">
                    {{ t('software.features.tournament') }}
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport>
                    {{ t('software.features.mouseLock') }}
                </BaseTagSupport>
            </ElDescriptionsItem>
            <ElDescriptionsItem :label="t('software.platform')">
                <BaseTagSupport>
                    <BaseBadgeOpenms />
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport>
                    <BaseBadgeSaolei />
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport>
                    <BaseBadgeMsgames />
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport>
                    <BaseBadgeScoreganizer />
                </BaseTagSupport>
            </ElDescriptionsItem>
        </ElDescriptions>
        <ElRow style="height: 1em" />
        <ElTable :data="tableData" table-layout="auto" style="max-width: 600px">
            <ElTableColumn prop="version" :label="t('software.version')" />
            <ElTableColumn prop="date" :label="t('software.releaseDate')" />
            <ElTableColumn :label="t('software.download')">
                <template #default="{row}">
                    <template v-for="link in row.links" :key="link.url">
                        <ElLink :href="link.url" target="_blank" rel="noopener noreferrer">
                            {{ link.label }}
                        </ElLink>
                        &nbsp;
                    </template>
                </template>
            </ElTableColumn>
        </ElTable>
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import { ElDescriptions, ElDescriptionsItem, ElLink, ElRow, ElTable, ElTableColumn } from 'element-plus';
import { useI18n } from 'vue-i18n';

import { BaseBadgeMsgames, BaseBadgeOpenms, BaseBadgeSaolei, BaseBadgeScoreganizer } from '@/components/common/badge';
import BaseTagSupport from '@/components/common/BaseTagSupport.vue';
import { BaseFlagCN, BaseFlagJP, BaseFlagUK } from '@/components/common/flag';

const tableData = [
    {
        version: '0.52.3',
        date: 'Unknown',
        links: [
            {
                label: 'OpenMS',
                url: 'https://openms.top/download/Arbiter_0.52.3.zip',
            },
            {
                label: 'Saolei',
                url: 'http://saolei.wang/Download/Arbiter_0.52.3.zip',
            },
            {
                label: 'MSGames',
                url: 'https://minesweepergame.com/download/arbiter.zip',
            },
        ],
    },
];

/* 本地化 Localization */
const i18nMessages = {
    'zh-cn': { local: {
        description: 'Minesweeper Arbiter 是最流行的专业扫雷软件。',
    } },
    'en': { local: {
        description: 'Minesweeper Arbiter is the most popular authoritative minesweeper clone.',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>
