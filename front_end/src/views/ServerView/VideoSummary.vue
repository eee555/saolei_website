<template>
    <base-card-normal style="display: flex; flex-direction: column;">
        <div style="text-align: center; margin-top: 0; font-size: 20px; font-weight: bold;">
            {{ t('server.videoSummary.title') }}
        </div>
        <div style="display: grid; grid-template-columns: 1fr; grid-gap: 1rem;">
            <VueUiSparkStackbar :dataset="softwareStackBarData" :config="getConfig('software')" />
            <VueUiSparkStackbar :dataset="levelStackBarData" :config="getConfig('level')" />
            <VueUiSparkStackbar :dataset="modeStackBarData" :config="getConfig('mode')" />
            <VueUiSparkStackbar :dataset="stateStackBarData" :config="getConfig('state')" />
        </div>
    </base-card-normal>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { VueUiSparkStackbar, VueUiSparkStackbarConfig } from 'vue-data-ui';
import { useI18n } from 'vue-i18n';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { local } from '@/store';
import { createEnumMap, EnumMap } from '@/utils';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { MS_Level, MS_Levels, MS_Mode, MS_Software, MS_Softwares, MS_State } from '@/utils/ms_const';

const { proxy } = useCurrentInstance();
const { t } = useI18n();

interface VideoSummary {
    total: number;
    software: EnumMap<MS_Software, number>;
    level: EnumMap<MS_Level, number>;
    mode: EnumMap<MS_Mode, number>;
    state: EnumMap<MS_State, number>;
}

const videoSummaryData = ref<VideoSummary>({
    total: 0,
    software: createEnumMap(MS_Softwares, 0),
    level: createEnumMap(MS_Levels, 0),
    mode: createEnumMap(Object.values(MS_Mode), 0),
    state: createEnumMap(Object.values(MS_State), 0),
});

const loading = ref(false);

function refresh() {
    loading.value = true;
    proxy.$axios.get('/common/api/videosummary').then((response) => {
        Object.assign(videoSummaryData.value, response.data);
        loading.value = false;
    });
}

onMounted(refresh);

const softwareStackBarData = computed(() => MS_Softwares.map((software) => ({
    name: t(`common.software.${software}`), // 动态拼接翻译键
    value: videoSummaryData.value.software[software],
})));

const levelStackBarData = computed(() => MS_Levels.map((level) => ({
    name: t(`common.level.${level}`), // 动态拼接翻译键
    value: videoSummaryData.value.level[level],
})));

const modeStackBarData = computed(() => Object.values(MS_Mode).map((mode) => ({
    name: t(`common.mode.code${mode}`), // 动态拼接翻译键
    value: videoSummaryData.value.mode[mode],
})));

const stateStackBarData = computed(() => Object.values(MS_State).map((state) => ({
    name: t(`common.state.${state}`), // 动态拼接翻译键
    value: videoSummaryData.value.state[state],
})));

function getConfig(prop: string) {
    return {
        loading: loading.value,
        theme: local.value.darkmode ? 'dark' : '',
        style: {
            title: {
                text: ' ',
                subtitle: {
                    text: t(`common.prop.${prop}`),
                },
            },
        },
    } as VueUiSparkStackbarConfig;
}

</script>
