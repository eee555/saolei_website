<template>
    <el-descriptions :title="t('local.appearance')" :column="3">
        <el-descriptions-item :label="t('local.colorscheme')" style="vertical-align: middle;">
            <DarkMode />
        </el-descriptions-item>
        <el-descriptions-item :label="t('local.languageSwitch')">
            <el-switch
                v-model="local.language_show"
                :active-text="t('common.show')" :inactive-text="t('common.hide')"
            />
        </el-descriptions-item>
        <el-descriptions-item :label="t('local.viennaLogo')">
            <el-switch v-model="local.vienna_logo_legacy">
                <template #active>
                    <Tippy :duration="0">
                        <img style="width: 16px; height: 16px" :src="ViennaIconLegacy">
                        <template #content>
                            {{ t('common.old') }}
                        </template>
                    </Tippy>
                </template>
                <template #inactive>
                    <Tippy :duration="0">
                        <img style="width: 16px; height: 16px" :src="ViennaIconNew">
                        <template #content>
                            {{ t('common.new') }}
                        </template>
                    </Tippy>
                </template>
            </el-switch>
        </el-descriptions-item>
        <el-descriptions-item :label="t('local.menuLayout')">
            <el-switch
                v-model="local.menu_icon"
                :active-text="t('local.menuLayoutAbstract')"
                :inactive-text="t('local.menuLayoutDefault')"
            />
        </el-descriptions-item>
        <el-descriptions-item :label="t('local.menuHeight')">
            <el-slider
                v-model="local.menu_height" size="small" :min="20" :max="60"
                style="width: 100px; display: inline-block; height: 9px"
            />
        </el-descriptions-item>
        <el-descriptions-item :label="t('local.menuFontSize')">
            <el-input-number
                v-model="local.menu_font_size"
                size="small" :min="10"
            />
        </el-descriptions-item>
        <el-descriptions-item :label="t('local.notificationDuration')">
            <base-tooltip>
                <el-input-number v-model="local.notification_duration" size="small" :min="0" :step="1000" />
                <template #content>
                    <span class="text">
                        {{ t('local.notificationDurationTooltip1') }}
                        <br>
                        {{ t('local.notificationDurationTooltip2') }}
                    </span>
                </template>
            </base-tooltip>
        </el-descriptions-item>
        <el-descriptions-item :label="t('local.newUserGuide')">
            <base-tooltip>
                <el-switch v-model="local.tooltip_show" />
                <template #content>
                    <span class="text">
                        {{ t('local.newUserGuideTooltip') }}
                    </span>
                </template>
            </base-tooltip>
        </el-descriptions-item>
        <el-descriptions-item :label="t('local.experimentalFeature')">
            <el-switch v-model="local.experimental" />
        </el-descriptions-item>
    </el-descriptions>
    <ExperimentalFeature>
        <el-descriptions :title="t('local.stnbConst')">
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
        <el-descriptions :title="t('local.visualizationColorScheme')">
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
</template>

<script lang="ts" setup name="UserSettings">
import { ElDescriptions, ElDescriptionsItem, ElInputNumber, ElOption, ElSelect, ElSlider, ElSwitch } from 'element-plus';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Tippy } from 'vue-tippy';

import '@/styles/text.css';
import BaseTooltip from '@/components/common/BaseTooltip.vue';
import ExperimentalFeature from '@/components/ExperimentalFeature.vue';
import ColorSchemeSetting from '@/components/visualization/ColorSchemeSetting.vue';
import DarkMode from '@/components/widgets/DarkMode.vue';
import { colorTheme, local } from '@/store';
import { ViennaIconLegacy, ViennaIconNew } from '@/utils/assets';
import { STNB_const } from '@/utils/ms_const';

const colorSchemeName = ref<'bvs' | 'btime' | 'itime' | 'etime' | 'stnb'>('bvs');

const i18nMessages = {
    'zh-cn': { local: {
        appearance: '外观设置',
        colorscheme: '颜色主题',
        experimentalFeature: '实验功能',
        languageSwitch: '语言切换',
        menuFontSize: '菜单字号',
        menuHeight: '菜单高度',
        menuLayout: '菜单排版',
        menuLayoutAbstract: '抽象',
        menuLayoutDefault: '默认',
        newUserGuide: '新手引导',
        newUserGuideTooltip: '鼠标在各种地方悬停时获取帮助。',
        notificationDuration: '通知时长',
        notificationDurationTooltip1: '显示的时间，单位毫秒。',
        notificationDurationTooltip2: '值为0则不会自动关闭。',
        stnbConst: 'STNB常数',
        viennaLogo: 'RMV图标',
        visualizationColorScheme: '数据可视化 - 配色方案',
    } },
    'en': { local: {
        appearance: 'Appearance',
        colorscheme: 'Color scheme',
        experimentalFeature: 'Experimental Features',
        languageSwitch: 'Language Switch',
        menuFontSize: 'Menu Font Size',
        menuHeight: 'Menu Height',
        menuLayout: 'Menu Layout',
        menuLayoutAbstract: 'Abstract',
        menuLayoutDefault: 'Default',
        newUserGuide: 'Get Help',
        newUserGuideTooltip: 'Get help by hovering over components',
        notificationDuration: 'Notification Duration',
        notificationDurationTooltip1: 'Duration before close. ',
        notificationDurationTooltip2: 'It will not automatically close if set 0. ',
        stnbConst: 'STNB Constants',
        viennaLogo: 'RMV logo',
        visualizationColorScheme: 'Visualization - Color scheme',
    } },
};

const { t } = useI18n({
    messages: i18nMessages,
});

</script>
