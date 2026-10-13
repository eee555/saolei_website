<template>
    <BaseOverlay>
        {{ t('common.software.software_download') }}
        <template #header>
            {{ t('common.software.software_download') }}
        </template>
        <template #overlay>
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
            </ElTabs>
        </template>
    </BaseOverlay>
</template>

<script lang="ts" setup>
import { ElTabPane, ElTabs } from 'element-plus';
import { useI18n } from 'vue-i18n';

import analyzerIcon from '@/assets/video-analyzer.svg';
import BaseOverlay from '@/components/common/BaseOverlay.vue';
import AnalyzerHelper from '@/components/dialogs/AnalyzerHelper.vue';
import ArbiterHelper from '@/components/dialogs/ArbiterHelper.vue';
import MetasweeperHelper from '@/components/dialogs/MetasweeperHelper.vue';
import ViennaSweeperHelper from '@/components/dialogs/ViennaSweeperHelper.vue';
import SoftwareIcon from '@/components/widgets/SoftwareIcon.vue';

const { t } = useI18n();
</script>

<style lang="less" scoped>
:deep(.el-tabs__content) {
    overflow: auto;
}
</style>
