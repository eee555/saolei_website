<template>
    <div>
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; column-gap: 10px; align-items: center;">
            <!-- 选择排序模板 -->
            <div>
                <el-select v-model="BBBvSummaryConfig.template" size="small" style="width: 80px">
                    <el-option :label="t('common.prop.bvs')" value="bvs" />
                    <el-option :label="t('common.prop.time')" value="time" />
                    <el-option :label="t('common.prop.stnb')" value="stnb" />
                    <el-option :label="t('common.prop.ioe')" value="ioe" />
                    <el-option :label="t('common.prop.thrp')" value="thrp" />
                    <el-option :label="t('common.prop.path')" value="path" />
                    <el-option :label="t('local.customTemplate')" value="custom" />
                </el-select>
                <template v-if="BBBvSummaryConfig.template === 'custom'">
                    &nbsp;
                    <el-link class="text text-small" underline="always" @click="BBBvSummaryConfig.sortDesc = !BBBvSummaryConfig.sortDesc">
                        {{ BBBvSummaryConfig.sortDesc ? t('local.settingMax') : t('local.settingMin') }}
                    </el-link>
                    <el-select v-model="BBBvSummaryConfig.sortBy" size="small" style="width:65px; margin-left: 0.2em; margin-right: 0.2em">
                        <el-option :label="t('common.prop.time')" value="timems" />
                        <el-option :label="t('common.prop.ioe')" value="ioe" />
                        <el-option :label="t('common.prop.thrp')" value="thrp" />
                        <el-option :label="t('common.prop.path')" value="path" />
                        <el-option :label="t('common.prop.cls')" value="cls" />
                        <el-option :label="t('common.prop.ces')" value="ces" />
                        <el-option :label="t('common.prop.iome')" value="iome" />
                    </el-select>
                    <span class="text text-small">
                        {{ t('local.settingDisplayBy') }}
                    </span>
                    <el-select v-model="BBBvSummaryConfig.displayBy" size="small" style="width:6em; margin-left: 0.2em">
                        <el-option :label="t('common.prop.bvs')" value="bvs" />
                        <el-option :label="t('common.prop.time')" value="time" />
                        <el-option :label="t('common.prop.stnb')" value="stnb" />
                        <el-option :label="t('common.prop.ioe')" value="ioe" />
                        <el-option :label="t('common.prop.thrp')" value="thrp" />
                        <el-option :label="t('common.prop.cls')" value="cls" />
                        <el-option :label="t('common.prop.ces')" value="ces" />
                        <el-option :label="t('common.prop.iome')" value="iome" />
                        <el-option :label="t('common.prop.path')" value="path" />
                        <el-option :label="t('common.prop.file_size')" value="file_size" />
                    </el-select>
                </template>
            </div>
            <!-- 软件筛选 -->
            <SoftwareFilter v-model="BBBvSummaryConfig.softwareFilter" />
            <!-- 是否显示图标 -->
            <div>
                <span class="text text-small">
                    图标
                </span>
                <el-select v-model="BBBvSummaryConfig.showIcon" size="small" placeholder="" style="width: 4em">
                    <el-option label="无" value="" />
                    <el-option :label="t('common.prop.software')" value="software" />
                    <el-option :label="t('common.prop.state')" value="state" />
                </el-select>
            </div>
            <!-- 点击格子的模式 -->
            <base-tooltip follow-cursor>
                <el-link
                    underline="always"
                    @click="BBBvSummaryConfig.tooltipMode === 'fast' ? BBBvSummaryConfig.tooltipMode = 'advanced' : BBBvSummaryConfig.tooltipMode = 'fast'"
                >
                    {{ t(`local.${BBBvSummaryConfig.tooltipMode}`) }}
                </el-link>
                <template #content>
                    {{ t(`local.${BBBvSummaryConfig.tooltipMode}Tooltip`) }}
                </template>
            </base-tooltip>
            <!-- 显示比例 -->
            <Zoomer v-model="BBBvSummaryConfig.zoom" />
        </div>
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ElLink, ElOption, ElSelect } from 'element-plus';
import { useI18n } from 'vue-i18n';

import BaseTooltip from '@/components/common/BaseTooltip.vue';
import SoftwareFilter from '@/components/Filters/SoftwareFilter.vue';
import Zoomer from '@/components/widgets/Zoomer.vue';
import { BBBvSummaryConfig } from '@/store';

/* 本地化 Localization */
const i18nMessage = {
    'zh-cn': { local: {
        customTemplate: '自定义',
        settingDisplayBy: '录像的',
        settingMax: '最大',
        settingMin: '最小',
        fast: '简易模式',
        fastTooltip: '点击播放录像',
        advanced: '高级模式',
        advancedTooltip: '点击显示录像列表，悬浮窗中播放录像',
    } },
    'en': { local: {
        customTemplate: 'Custom',
        settingDisplayBy: 'and display by',
        settingMax: 'Find max',
        settingMin: 'Find min',
        fast: 'Fast',
        fastTooltip: 'Click to play the video',
        advanced: 'Advanced',
        advancedTooltip: 'Click to show list of videos',
    } },
};

const { t } = useI18n({ messages: i18nMessage });
</script>

<style lang="less" scoped>

.el-select-dropdown__item {
    height: 25px;
    line-height: 25px;
}

</style>
