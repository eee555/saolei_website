<template>
    <ElTabs tab-position="left" style="height: 350px; width: 700px; justify-self: center;">
        <ElTabPane>
            <template #label>
                <SoftwareIcon software="e" />
            </template>
            <MetasweeperHelper />
        </ElTabPane>
        <ElTabPane>
            <template #label>
                <SoftwareIcon software="a" />
            </template>
            <ArbiterHelper />
        </ElTabPane>
        <ElTabPane>
            <template #label>
                <SoftwareIcon software="r" />
            </template>
            <ViennaSweeperHelper />
        </ElTabPane>
        <ElTabPane name="analyzer" label="Analyzer">
            <template #label>
                <img :src="analyzerIcon" alt="Analyzer" title="OpenMinesweeper Video Analyzer" width="16" height="16">
            </template>
            <AnalyzerHelper />
        </ElTabPane>
        <ElTabPane name="yuanshen-toolbox" :label="t('local.yuanshenToolbox')">
            <template #label>
                <img :src="yuanshenToolboxIcon" :alt="t('local.yuanshenToolbox')" :title="t('local.yuanshenToolbox')" width="16" height="16">
            </template>
            <YuanshenToolboxHelper />
        </ElTabPane>
    </ElTabs>
</template>

<script lang="ts" setup>
import { ElTabPane, ElTabs } from 'element-plus';
import { useI18n } from 'vue-i18n';

import yuanshenToolboxIcon from '@/assets/img/yuanshen-toolbox.png';
import analyzerIcon from '@/assets/video-analyzer.svg';
import AnalyzerHelper from '@/components/dialogs/AnalyzerHelper.vue';
import ArbiterHelper from '@/components/dialogs/ArbiterHelper.vue';
import MetasweeperHelper from '@/components/dialogs/MetasweeperHelper.vue';
import ViennaSweeperHelper from '@/components/dialogs/ViennaSweeperHelper.vue';
import YuanshenToolboxHelper from '@/components/dialogs/YuanshenToolboxHelper.vue';
import SoftwareIcon from '@/components/widgets/SoftwareIcon.vue';

const i18nMessages = {
    'zh-cn': { local: {
        yuanshenToolbox: '元神工具箱',
    } },
    en: { local: {
        yuanshenToolbox: 'Yuanshen Toolbox',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>

<style lang="less" scoped>
:deep(.el-tabs__content) {
    overflow: auto;
}
</style>
