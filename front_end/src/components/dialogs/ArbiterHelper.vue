<template>
    <div>
        <el-text size="large">
            {{ t('software.arbiterDescription') }}
        </el-text>
        <el-row style="height: 1em" />
        <el-descriptions border style="max-width: 600px">
            <el-descriptions-item :label="t('software.operatingSystem')" :span="2">
                Windows
            </el-descriptions-item>
            <el-descriptions-item :label="t('software.supportedLanguages')">
                <BaseFlagUK />&nbsp;<BaseFlagCN />&nbsp;<BaseFlagJP />
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
            </el-descriptions-item>
            <el-descriptions-item :label="t('software.platform')">
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
            </el-descriptions-item>
        </el-descriptions>
        <el-row style="height: 1em" />
        <el-table :data="tableData" table-layout="auto" style="max-width: 600px">
            <el-table-column prop="version" :label="t('software.version')" />
            <el-table-column prop="date" :label="t('software.releaseDate')" />
            <el-table-column :label="t('software.download')">
                <template #default="{row}">
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
import { BaseFlagCN, BaseFlagJP, BaseFlagUK } from '@/components/common/flag';

const { t } = useI18n();

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

</script>
