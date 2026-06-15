<template>
    <ElCard :header="t('local.visualizationColorScheme')">
        <div style="display: flex; flex-direction: column; gap: 1rem">
            <div style="display: flex; flex-wrap: wrap; gap: 2rem; align-items: center">
                <div class="text">
                    {{ t('local.level') }}
                </div>
                <span v-for="level in ['b', 'i', 'e']" style="display: flex; gap: 0.5em">
                    <span class="text">
                        {{ t(`common.level.${level}`) }}
                    </span>
                    <ElColorPicker v-model="colorTheme.level[level]" size="small" />
                </span>
            </div>
            <div v-experimental style="display: flex; flex-direction: column; gap: 0.5rem;">
                <div class="text">
                    {{ t('local.piecewise') }}
                </div>
                <ElSelect v-model="colorSchemeName">
                    <ElOption label="Bvs" value="bvs" />
                    <ElOption label="Beg Time" value="btime" />
                    <ElOption label="Int Time" value="itime" />
                    <ElOption label="Exp Time" value="etime" />
                    <ElOption label="STNB" value="stnb" />
                </ElSelect>
                <ColorSchemeSetting v-model="colorTheme[colorSchemeName]" />
            </div>
        </div>
    </ElCard>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ElCard, ElColorPicker, ElOption, ElSelect } from 'element-plus';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { vExperimental } from '@/components/ExperimentalFeature';
import ColorSchemeSetting from '@/components/visualization/ColorSchemeSetting.vue';
import { colorTheme } from '@/store';

const colorSchemeName = ref<'bvs' | 'btime' | 'itime' | 'etime' | 'stnb'>('bvs');

const i18nMessages = {
    'zh-cn': { local: {
        level: '各级别主色',
        piecewise: '分段色阶',
        visualizationColorScheme: '数据可视化 - 配色方案',
    } },
    'en': { local: {
        level: 'Primary Colors for Levels',
        piecewise: 'Piecewise Palette',
        visualizationColorScheme: 'Visualization - Color Scheme',
    } },
};

const { t } = useI18n({
    messages: i18nMessages,
});
</script>

<style lang="less" scoped>
.card-body {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
</style>
