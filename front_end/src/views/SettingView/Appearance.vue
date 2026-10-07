<template>
    <section class="card">
        <h2 class="card-title">
            {{ t('local.appearance') }}
        </h2>
        <div class="description-layout">
            <dl class="descriptions">
                <div class="description-item">
                    <dt>{{ t('local.colorscheme') }}</dt>
                    <dd>
                        <DarkMode />
                    </dd>
                </div>
                <div class="description-item">
                    <dt>{{ t('local.languageSwitch') }}</dt>
                    <dd>
                        <ElSwitch
                            v-model="local.language_show"
                            :active-text="t('common.show')" :inactive-text="t('common.hide')"
                        />
                    </dd>
                </div>
                <div class="description-item">
                    <dt>{{ t('local.viennaLogo') }}</dt>
                    <dd>
                        <ElSwitch v-model="local.vienna_logo_legacy">
                            <template #active>
                                <img style="width: 16px; height: 16px" :src="ViennaIconLegacy" :title="t('common.old')">
                            </template>
                            <template #inactive>
                                <img style="width: 16px; height: 16px" :src="ViennaIconNew" :title="t('common.new')">
                            </template>
                        </ElSwitch>
                    </dd>
                </div>
                <div class="description-item">
                    <dt>{{ t('local.menuLayout') }}</dt>
                    <dd>
                        <ElSwitch
                            v-model="local.menu_icon"
                            :active-text="t('local.menuLayoutAbstract')"
                            :inactive-text="t('local.menuLayoutDefault')"
                        />
                    </dd>
                </div>
                <div class="description-item">
                    <dt>{{ t('local.menuHeight') }}</dt>
                    <dd>
                        <ElSlider
                            v-model="local.menu_height" size="small" :min="20" :max="60"
                            style="width: 100px; display: inline-block; height: 9px"
                        />
                    </dd>
                </div>
                <div class="description-item">
                    <dt>{{ t('local.menuFontSize') }}</dt>
                    <dd>
                        <ElInputNumber
                            v-model="local.menu_font_size"
                            size="small" :min="10"
                        />
                    </dd>
                </div>
                <div class="description-item">
                    <dt>{{ t('local.notificationDuration') }}</dt>
                    <dd>
                        <BaseTooltip>
                            <ElInputNumber v-model="local.notification_duration" size="small" :min="0" :step="1000" />
                            <template #content>
                                <span class="text-regular">
                                    {{ t('local.notificationDurationTooltip1') }}
                                    <br>
                                    {{ t('local.notificationDurationTooltip2') }}
                                </span>
                            </template>
                        </BaseTooltip>
                    </dd>
                </div>
                <div class="description-item">
                    <dt>{{ t('local.nameFormat') }}</dt>
                    <dd>
                        <span :title="t('local.nameFormatTooltip')">
                            <ElRadioGroup v-model="local.nameFormat" size="small" style="vertical-align: middle;">
                                <ElRadioButton :label="t('local.nameFormatFirstLast')" value="first-last" />
                                <ElRadioButton :label="t('local.nameFormatLastFirst')" value="last-first" />
                            </ElRadioGroup>
                        </span>
                    </dd>
                </div>
                <div class="description-item">
                    <dt>{{ t('local.newUserGuide') }}</dt>
                    <dd>
                        <span :title="t('local.newUserGuideTooltip')">
                            <ElSwitch v-model="local.tooltip_show" />
                        </span>
                    </dd>
                </div>
                <div class="description-item description-wide">
                    <dt>{{ t('local.experimentalFeature') }}</dt>
                    <dd>
                        <ElSwitch v-model="local.experimental" />
                    </dd>
                </div>
            </dl>
        </div>
    </section>
</template>

<script setup lang="ts">
import '@/styles/descriptions.css';
import '@/styles/cards.css';
import '@/styles/text.css';

import { ElInputNumber, ElRadioButton, ElRadioGroup, ElSlider, ElSwitch } from 'element-plus';
import { useI18n } from 'vue-i18n';

import BaseTooltip from '@/components/common/BaseTooltip.vue';
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
    en: { local: {
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
