<template>
    <el-table-column width="32">
        <template #default="{row}: {row: VideoAbstract}">
            <base-overlay>
                <SoftwareIcon :software="row.software" style="margin: 0 -8px;" />
                <template #header>
                    <template v-if="row.software === 'e'">
                        <img style="width: 24px; height: 24px; vertical-align: middle;" src="@/assets/img/img_meta.png">
                        {{ t('software.metasweeper') }}
                    </template>
                    <template v-else-if="row.software === 'a'">
                        <img style="width: 24px; height: 24px; vertical-align: middle;" src="@/assets/img/ms_arbiter_MAINICON.ico">
                        {{ t('software.arbiter') }}
                    </template>
                </template>
                <template #overlay>
                    <MetasweeperHelper v-if="row.software == 'e'" style="justify-self: center;" />
                    <ArbiterHelper v-else-if="row.software == 'a'" style="justify-self: center;" />
                </template>
            </base-overlay>
        </template>
    </el-table-column>
</template>

<script setup lang="ts">

import { ElTableColumn } from 'element-plus';
import { defineAsyncComponent } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseOverlay from '@/components/common/BaseOverlay.vue';
import SoftwareIcon from '@/components/widgets/SoftwareIcon.vue';
import { VideoAbstract } from '@/utils/videoabstract';

const MetasweeperHelper = defineAsyncComponent(() => import('@/components/dialogs/MetasweeperHelper.vue'));
const ArbiterHelper = defineAsyncComponent(() => import('@/components/dialogs/ArbiterHelper.vue'));

const { t } = useI18n();

</script>
