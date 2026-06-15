<template>
    <el-card :header="t('local.appearance')">
        <el-descriptions>
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
                        <img style="width: 16px; height: 16px" :src="ViennaIconLegacy" :title="t('common.old')">
                    </template>
                    <template #inactive>
                        <img style="width: 16px; height: 16px" :src="ViennaIconNew" :title="t('common.new')">
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
            <el-descriptions-item :label="t('local.nameFormat')">
                <span :title="t('local.nameFormatTooltip')">
                    <el-radio-group v-model="local.nameFormat" size="small" style="vertical-align: middle;">
                        <el-radio-button :label="t('local.nameFormatFirstLast')" value="first-last" />
                        <el-radio-button :label="t('local.nameFormatLastFirst')" value="last-first" />
                    </el-radio-group>
                </span>
            </el-descriptions-item>
            <el-descriptions-item :label="t('local.newUserGuide')">
                <span :title="t('local.newUserGuideTooltip')">
                    <el-switch v-model="local.tooltip_show" />
                </span>
            </el-descriptions-item>
            <el-descriptions-item :label="t('local.experimentalFeature')">
                <el-switch v-model="local.experimental" />
            </el-descriptions-item>
        </el-descriptions>
    </el-card>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ElCard, ElDescriptions, ElDescriptionsItem, ElInputNumber, ElRadioButton, ElRadioGroup, ElSlider, ElSwitch } from 'element-plus';
import { useI18n } from 'vue-i18n';

import DarkMode from '@/components/widgets/DarkMode.vue';
import { local } from '@/store';
import { ViennaIconLegacy, ViennaIconNew } from '@/utils/assets';

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
        nameFormat: '姓名格式',
        nameFormatFirstLast: '名 姓',
        nameFormatLastFirst: '姓, 名',
        nameFormatTooltip: '英文名显示格式',
        newUserGuide: '新手引导',
        newUserGuideTooltip: '鼠标在各种地方悬停时获取帮助。',
        notificationDuration: '通知时长',
        notificationDurationTooltip1: '显示的时间，单位毫秒。',
        notificationDurationTooltip2: '值为0则不会自动关闭。',
        viennaLogo: 'RMV图标',
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
        nameFormat: 'Name Format',
        nameFormatFirstLast: 'Given Family',
        nameFormatLastFirst: 'Family, Given',
        nameFormatTooltip: 'Display format for international names',
        newUserGuide: 'Get Help',
        newUserGuideTooltip: 'Get help by hovering over components',
        notificationDuration: 'Notification Duration',
        notificationDurationTooltip1: 'Duration before close. ',
        notificationDurationTooltip2: 'It will not automatically close if set 0. ',
        viennaLogo: 'RMV logo',
    } },
};

const { t } = useI18n({
    messages: i18nMessages,
});
</script>
