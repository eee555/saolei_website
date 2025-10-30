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
                        <BaseIconMetasweeper />
                    </template>
                    <MetasweeperHelper />
                </el-tab-pane>
                <el-tab-pane>
                    <template #label>
                        <BaseIconArbiter />
                    </template>
                    <ArbiterHelper />
                </el-tab-pane>
            </el-tabs>
        </template>
    </base-overlay>
</template>

<script lang="ts" setup>
import { ElTabPane, ElTabs } from 'element-plus';
import { useI18n } from 'vue-i18n';

import BaseIconArbiter from '@/components/common/BaseIconArbiter.vue';
import BaseIconMetasweeper from '@/components/common/BaseIconMetasweeper.vue';
import BaseOverlay from '@/components/common/BaseOverlay.vue';
import ArbiterHelper from '@/components/dialogs/ArbiterHelper.vue';
import MetasweeperHelper from '@/components/dialogs/MetasweeperHelper.vue';

const { t } = useI18n();

</script>

<style lang="less" scoped>
:deep(.el-tabs__content) {
    overflow: auto;
}
</style>
