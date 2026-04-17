<template>
    <div>
        <span class="text text-medium">
            {{ t('local.description1') }}
            <br>
            {{ t('local.description2') }}
            <br>
            {{ t('software.officialSite') }}{{ t('common.punct.colon') }}
            https://sweeper.wien
        </span>
        <el-row style="height: 1em" />
        <el-descriptions border>
            <el-descriptions-item :label="t('software.operatingSystem')" :span="2">
                Windows
            </el-descriptions-item>
            <el-descriptions-item :label="t('software.supportedLanguages')">
                <BaseFlagUK />
            </el-descriptions-item>
            <el-descriptions-item :label="t('software.feature')" :span="3">
                <BaseTagSupport>
                    {{ t('software.features.customMode') }}
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport :support="false">
                    {{ t('software.features.customCounter') }}
                </BaseTagSupport>
                &nbsp;
                <BaseTagSupport :support="false">
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
                <BaseTagSupport :support="false">
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
        <el-table :data="tableData" table-layout="auto">
            <el-table-column prop="version" :label="t('software.version')" />
            <el-table-column prop="date" :label="t('software.releaseDate')" />
            <el-table-column prop="expire" :label="t('software.expireDate')" />
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
import '@/styles/text.css';
import { ElDescriptions, ElDescriptionsItem, ElLink, ElRow, ElTable, ElTableColumn } from 'element-plus';
import { useI18n } from 'vue-i18n';

import { BaseBadgeMsgames, BaseBadgeOpenms, BaseBadgeSaolei, BaseBadgeScoreganizer } from '@/components/common/badge';
import BaseTagSupport from '@/components/common/BaseTagSupport.vue';
import { BaseFlagUK } from '@/components/common/flag';

const tableData = [
    {
        version: 'v4.0.0',
        date: '2024-11-15',
        expire: '-',
        links: [
            {
                label: 'Official',
                url: 'https://sweeper.wien/static/downloads/vsweep-4.0.0-vsh-0.1.0.zip',
            },
        ],
    },
    {
        version: 'v5.0.0b4',
        date: '2025-9-7',
        expire: 'Beta',
        links: [
            {
                label: 'Official',
                url: 'https://sweeper.wien/static/downloads/vsweep-5.0.0b4-vsh-0.2.0b2.zip',
            },
        ],
    },
    {
        version: 'v3.0',
        date: 'Unknown',
        expire: '2023-4-24',
        links: [
            {
                label: 'Saolei',
                url: 'http://saolei.wang/Download/Viennasweeper_3.0.zip',
            },
        ],
    },
];

const i18nMessages = {
    'zh-cn': { local: {
        description1: 'Viennasweeper 是一款专业扫雷软件，它和Scoreganizer的兼容性最好。',
        description2: '从v5.0.0版本开始，Viennasweeper使用了新的录像格式，该格式目前仅被开源扫雷网和Scoreganizer支持。',
    } },
    'en': { local: {
        description1: 'Viennasweeper is an official minesweeper clone. It has the best compatibility with Scoreganizer.',
        description2: 'From v5.0.0, Viennasweeper moves to a new replay format that is only currently supported by Open Minesweeper and Scoreganizer.',
    } },
};

const { t } = useI18n({
    messages: i18nMessages,
});

</script>
