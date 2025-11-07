<template>
    <PrColumn>
        <template #body="{data}: {data: VideoAbstract}">
            <base-overlay>
                <SoftwareIcon :software="data.software" style="margin: 0 -8px;" />
                <template #header>
                    <template v-if="data.software === 'e'">
                        <img style="width: 24px; height: 24px; vertical-align: middle;" src="@/assets/img/img_meta.png">
                        {{ t('software.metasweeper') }}
                    </template>
                    <template v-else-if="data.software === 'a'">
                        <img style="width: 24px; height: 24px; vertical-align: middle;" src="@/assets/img/ms_arbiter_MAINICON.ico">
                        {{ t('software.arbiter') }}
                    </template>
                </template>
                <template #overlay>
                    <MetasweeperHelper v-if="data.software == 'e'" style="justify-self: center;" />
                    <ArbiterHelper v-else-if="data.software == 'a'" style="justify-self: center;" />
                </template>
            </base-overlay>
        </template>
    </PrColumn>
</template>

<script setup lang="ts">

import PrColumn from 'primevue/column';
import { defineAsyncComponent } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseOverlay from '@/components/common/BaseOverlay.vue';
import SoftwareIcon from '@/components/widgets/SoftwareIcon.vue';
import { VideoAbstract } from '@/utils/videoabstract';

const MetasweeperHelper = defineAsyncComponent(() => import('@/components/dialogs/MetasweeperHelper.vue'));
const ArbiterHelper = defineAsyncComponent(() => import('@/components/dialogs/ArbiterHelper.vue'));

const { t } = useI18n();

</script>
