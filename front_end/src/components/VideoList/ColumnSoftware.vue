<template>
    <PrColumn field="software" :show-filter-match-modes="false" :show-filter-operator="false" :show-apply-button="false" :show-clear-button="false">
        <template #body="{data}: {data: VideoAbstract}">
            <base-overlay>
                <SoftwareIcon :software="data.software" style="margin: 0 -8px;" />
                <template #header>
                    <template v-if="data.software === 'e'">
                        <img style="width: 24px; height: 24px; vertical-align: middle;" :src="MetasweeperIcon">
                        {{ t('software.metasweeper') }}
                    </template>
                    <template v-else-if="data.software === 'a'">
                        <img style="width: 24px; height: 24px; vertical-align: middle;" :src="ArbiterIcon">
                        {{ t('software.arbiter') }}
                    </template>
                </template>
                <template #overlay>
                    <MetasweeperHelper v-if="data.software == 'e'" style="justify-self: center;" />
                    <ArbiterHelper v-else-if="data.software == 'a'" style="justify-self: center;" />
                </template>
            </base-overlay>
        </template>
        <template #filter="{ filterModel, applyFilter }">
            <PrListbox v-model="filterModel.value" multiple :options="[...MS_Softwares]" @change="applyFilter()">
                <template #option="slotProps">
                    {{ t(`common.software.${slotProps.option}`) }}
                </template>
            </PrListbox>
        </template>
    </PrColumn>
</template>

<script setup lang="ts">
import PrColumn from 'primevue/column';
import PrListbox from 'primevue/listbox';
import { defineAsyncComponent } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseOverlay from '@/components/common/BaseOverlay.vue';
import SoftwareIcon from '@/components/widgets/SoftwareIcon.vue';
import { ArbiterIcon, MetasweeperIcon } from '@/utils/assets';
import { MS_Softwares } from '@/utils/ms_const';
import { VideoAbstract } from '@/utils/videoabstract';

const MetasweeperHelper = defineAsyncComponent(() => import('@/components/dialogs/MetasweeperHelper.vue'));
const ArbiterHelper = defineAsyncComponent(() => import('@/components/dialogs/ArbiterHelper.vue'));

const { t } = useI18n();
</script>
