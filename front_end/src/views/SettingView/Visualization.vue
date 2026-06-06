<template>
    <el-card :header="t('local.visualizationColorScheme')">
        <div v-experimental>
            <div class="text text-large">
                {{ t('local.piecewise') }}
            </div>
            <el-select v-model="colorSchemeName">
                <el-option label="Bvs" value="bvs" />
                <el-option label="Beg Time" value="btime" />
                <el-option label="Int Time" value="itime" />
                <el-option label="Exp Time" value="etime" />
                <el-option label="STNB" value="stnb" />
            </el-select>
            <ColorSchemeSetting v-model="colorTheme[colorSchemeName]" />
        </div>
        <div style="width: 100%; display: flex; flex-wrap: wrap">
            <div class="text text-large">
                {{ t('local.level') }}
            </div>
            <span v-for="level in ['b', 'i', 'e']">
                <span class="text">
                    {{ t(`common.level.${level}`) }}
                </span>
                <ElColorPicker v-model="colorTheme.level[level]" size="small" />
            </span>
        </div>
    </el-card>
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
        level: 'Primary Color for Each Level',
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
