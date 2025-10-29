<template>
    <div>
        <el-text size="large">
            {{ t('software.metaDescription') }}
            <br>
            {{ t('software.repository') }}{{ t('common.punct.colon') }}
            https://github.com/eee555/Metasweeper
        </el-text>
        <el-row style="height: 1em" />
        <el-descriptions border>
            <el-descriptions-item :label="t('software.operatingSystem')" :span="2">
                Windows
            </el-descriptions-item>
            <el-descriptions-item :label="t('software.supportedLanguages')">
                <BaseFlagCN />&nbsp;
                <BaseFlagUK />&nbsp;
                <BaseFlagPL />&nbsp;
                <BaseFlagDE />
            </el-descriptions-item>
            <el-descriptions-item :label="t('software.feature')" :span="3">
                <BaseTagSupport>
                    {{ t('software.features.customMode') }}
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport>
                    {{ t('software.features.customCounter') }}
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport>
                    {{ t('software.features.noGuessing') }}
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport>
                    {{ t('software.features.cellScale') }}
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport>
                    {{ t('software.features.tournament') }}
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport>
                    {{ t('software.features.mouseLock') }}
                </BaseTagSupport>
            </el-descriptions-item>
            <el-descriptions-item :label="t('software.platform')">
                <BaseTagSupport>
                    <BaseBadgeOpenms />
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport :support="false">
                    <BaseBadgeSaolei />
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport :support="false">
                    <BaseBadgeMsgames />
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport :support="false">
                    <BaseBadgeScoreganizer />
                </BaseTagSupport>
            </el-descriptions-item>
        </el-descriptions>
        <el-row style="height: 1em" />
        <el-table :data="tableData" table-layout="auto">
            <el-table-column prop="version" :label="t('software.version')" />
            <el-table-column prop="date" :label="t('software.releaseDate')" />
            <el-table-column :label="t('software.download')">
                <template #default="{ row }">
                    <template v-for="link in row.links" :key="link.url">
                        <el-link :href="link.url" target="_blank">
                            {{ link.label }}
                        </el-link>
                        &nbsp;
                    </template>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

<script setup lang="ts">
import { ElDescriptions, ElDescriptionsItem, ElLink, ElRow, ElTable, ElTableColumn, ElText } from 'element-plus';
import { useI18n } from 'vue-i18n';

import { BaseBadgeMsgames, BaseBadgeOpenms, BaseBadgeSaolei, BaseBadgeScoreganizer } from '@/components/common/badge';
import BaseTagSupport from '@/components/common/BaseTagSupport.vue';
import { BaseFlagCN, BaseFlagDE, BaseFlagPL, BaseFlagUK } from '@/components/common/flag';

const { t } = useI18n();

const tableData = [
    {
        version: 'v3.2.0',
        date: '2024-11-21',
        links: [
            {
                label: 'Gitee',
                url: 'https://gitee.com/ee55/Metasweeper/releases/download/3.2.0/Metaminesweeper-3.2.0.exe',
            },
            {
                label: 'GitHub',
                url: 'https://github.com/eee555/Metasweeper/releases/download/3.2.0/Metaminesweeper-3.2.0.exe',
            },
        ],
    },
    {
        version: 'v3.1.11',
        date: '2024-9-10',
        links: [
            {
                label: 'OpenMS',
                url: 'https://openms.top/download/Metaminesweeper-v3.1.11.zip',
            },
            {
                label: 'GitHub',
                url: 'https://github.com/eee555/Metasweeper/releases/download/3.1.11/Metaminesweeper-v3.1.11.zip',
            },
        ],
    },
    {
        version: 'v3.1.9',
        date: '2024-7-27',
        links: [
            {
                label: 'OpenMS',
                url: 'https://openms.top/download/Metaminesweeper-v3.1.9.zip',
            },
            {
                label: 'GitHub',
                url: 'https://github.com/eee555/Metasweeper/releases/download/3.1.9/Metaminesweeper-v3.1.9.zip',
            },
        ],
    },
];

</script>
