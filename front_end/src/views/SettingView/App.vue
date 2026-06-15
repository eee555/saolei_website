<template>
    <div style="display: flex; flex-direction: column; gap: 1rem;">
        <Appearance />
        <ElCard :header="t('local.thirdPartyTrust')">
            <ElCheckbox v-model="videoPlayerConfig.strangeDustTrust">
                https://strange-dust.github.io/minesweeper-replay-analyzer/
            </ElCheckbox>
        </ElCard>
        <Visualization />
        <ElCard v-experimental :header="t('local.stnbConst')">
            <ElDescriptions>
                <ElDescriptionsItem :label="t('common.level.b')">
                    <ElInputNumber v-model="STNB_const.b" size="small" :controls="false" />
                </ElDescriptionsItem>
                <ElDescriptionsItem :label="t('common.level.i')">
                    <ElInputNumber v-model="STNB_const.i" size="small" :controls="false" />
                </ElDescriptionsItem>
                <ElDescriptionsItem :label="t('common.level.e')">
                    <ElInputNumber v-model="STNB_const.e" size="small" :controls="false" />
                </ElDescriptionsItem>
            </ElDescriptions>
        </ElCard>
    </div>
</template>

<script lang="ts" setup name="UserSettings">
import { ElCard, ElCheckbox, ElDescriptions, ElDescriptionsItem, ElInputNumber } from 'element-plus';
import { useI18n } from 'vue-i18n';

import Appearance from './Appearance.vue';
import Visualization from './Visualization.vue';

import { vExperimental } from '@/components/ExperimentalFeature';
import { videoPlayerConfig } from '@/store';
import { STNB_const } from '@/utils/ms_const';


const i18nMessages = {
    'zh-cn': { local: {
        stnbConst: 'STNB常数',
        thirdPartyTrust: '第三方网站信任列表',
    } },
    'en': { local: {
        stnbConst: 'STNB Constants',
        thirdPartyTrust: 'Third Party Trust List',
    } },
};

const { t } = useI18n({
    messages: i18nMessages,
});
</script>
