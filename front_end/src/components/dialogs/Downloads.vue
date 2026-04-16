<template>
    <base-overlay>
        {{ t('common.software.software_download') }}
        <template #header>
            {{ t('common.software.software_download') }}
        </template>
        <template #overlay>
            <el-tabs tab-position="left" style="height: 350px; width: 700px; justify-self: center;">
                <el-tab-pane>
                    <template #label>
                        <SoftwareIcon software="m" />
                    </template>
                    <MetasweeperHelper />
                </el-tab-pane>
                <el-tab-pane>
                    <template #label>
                        <SoftwareIcon software="a" />
                    </template>
                    <ArbiterHelper />
                </el-tab-pane>
                <el-tab-pane>
                    <template #label>
                        <SoftwareIcon software="r" />
                    </template>
                    <ViennaSweeperHelper />
                </el-tab-pane>
            </el-tabs>
        </template>
    </base-overlay>
</template>

<script lang="ts" setup>
import { ElTabPane, ElTabs } from 'element-plus';
import { useI18n } from 'vue-i18n';

import BaseOverlay from '@/components/common/BaseOverlay.vue';
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
