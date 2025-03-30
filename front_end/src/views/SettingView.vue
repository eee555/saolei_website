<template>
    <el-descriptions :title="t('setting.appearance')" :column="3">
        <el-descriptions-item :label="t('setting.colorscheme.title')" style="vertical-align: middle;">
            <DarkMode />
        </el-descriptions-item>
        <el-descriptions-item :label="t('setting.languageSwitch')">
            <el-switch
                v-model="local.language_show"
                :active-text="t('common.show')" :inactive-text="t('common.hide')"
            />
        </el-descriptions-item>
        <el-descriptions-item :label="t('setting.menuLayout')">
            <el-switch
                v-model="local.menu_icon"
                :active-text="t('setting.menuLayoutAbstract')"
                :inactive-text="t('setting.menuLayoutDefault')"
            />
        </el-descriptions-item>
        <el-descriptions-item :label="t('setting.menuHeight')">
            <el-slider
                v-model="local.menu_height" size="small" :min="20" :max="60"
                style="width: 100px; display: inline-block; height: 9px"
            />
        </el-descriptions-item>
        <el-descriptions-item :label="t('setting.menuFontSize')">
            <el-input-number
                v-model="local.menu_font_size"
                size="small" :min="10"
            />
        </el-descriptions-item>
        <el-descriptions-item :label="t('setting.notificationDuration')">
            <el-tooltip>
                <template #content>
                    <div v-html="t('setting.notificationDurationTooltip')" />
                </template>
                <el-input-number v-model="local.notification_duration" size="small" :min="0" :step="1000" />
            </el-tooltip>
        </el-descriptions-item>
        <el-descriptions-item :label="t('setting.newUserGuide')">
            <el-tooltip>
                <template #content>
                    <div v-html="t('setting.newUserGuideTooltip')" />
                </template>
                <el-switch v-model="local.tooltip_show" />
            </el-tooltip>
        </el-descriptions-item>
        <el-descriptions-item :label="t('setting.experimentalFeature')">
            <el-switch v-model="local.experimental" />
        </el-descriptions-item>
    </el-descriptions>
    <ExperimentalFeature>
        <el-descriptions title="STNB常数">
            <el-descriptions-item :label="t('common.level.b')">
                <el-input-number v-model="STNB_const.b" size="small" :controls="false" />
            </el-descriptions-item>
            <el-descriptions-item :label="t('common.level.i')">
                <el-input-number v-model="STNB_const.i" size="small" :controls="false" />
            </el-descriptions-item>
            <el-descriptions-item :label="t('common.level.e')">
                <el-input-number v-model="STNB_const.e" size="small" :controls="false" />
            </el-descriptions-item>
        </el-descriptions>
        <el-descriptions title="数据可视化 - 配色方案">
            <el-descriptions-item>
                <el-select v-model="colorSchemeName">
                    <el-option label="Bvs" value="bvs" />
                    <el-option label="Beg Time" value="btime" />
                    <el-option label="Int Time" value="itime" />
                    <el-option label="Exp Time" value="etime" />
                    <el-option label="STNB" value="stnb" />
                </el-select>
                <ColorSchemeSetting v-model="colorTheme[colorSchemeName]" />
            </el-descriptions-item>
        </el-descriptions>
    </ExperimentalFeature>
    <el-descriptions v-if="false && store.login_status == LoginStatus.IsLogin" title="个人信息" :column="3">
        <el-descriptions-item label="用户id">
            {{ store.user.id }}
        </el-descriptions-item>
        <el-descriptions-item label="用户名">
            {{ store.user.username }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.prop.realName')">
            {{ store.user.realname }}
        </el-descriptions-item>
        <el-descriptions-item label="英文姓">
            {{ t('common.toDo') }}
        </el-descriptions-item>
        <el-descriptions-item label="英文名">
            {{ t('common.toDo') }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.prop.sex')">
            {{ t('common.toDo') }}
        </el-descriptions-item>
        <el-descriptions-item label="属地">
            {{ t('common.toDo') }}
        </el-descriptions-item>
        <el-descriptions-item label="出生年份">
            {{ t('common.toDo') }}
        </el-descriptions-item>
    </el-descriptions>
</template>

<script lang="ts" setup name="UserSettings">
import { store, local, colorTheme } from '@/store';
import { ElDescriptions, ElDescriptionsItem, ElSelect, ElOption, ElTooltip, ElSwitch, ElSlider, ElInputNumber } from 'element-plus';
import { LoginStatus } from '@/utils/common/structInterface';
import { useI18n } from 'vue-i18n';
const { t } = useI18n()

import DarkMode from '@/components/widgets/DarkMode.vue'
import ColorSchemeSetting from '@/components/visualization/ColorSchemeSetting.vue'
import { ref } from 'vue';
import ExperimentalFeature from '@/components/ExperimentalFeature.vue';
import { STNB_const } from '@/utils/ms_const';

const colorSchemeName = ref('bvs');

</script>
