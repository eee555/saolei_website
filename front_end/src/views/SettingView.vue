<template>
    <el-descriptions :title="t.t('setting.appearance')" :column="3">
        <el-descriptions-item :label="t.t('setting.colorscheme.title')" style="vertical-align: middle;">
            <DarkMode />
        </el-descriptions-item>
        <el-descriptions-item :label="t.t('setting.languageSwitch')"><el-switch v-model="local.language_show"
                :active-text="$t('common.show')" :inactive-text="$t('common.hide')"></el-switch></el-descriptions-item>
        <el-descriptions-item :label="t.t('setting.menuLayout')"><el-switch v-model="local.menu_icon"
                :active-text="t.t('setting.menuLayoutAbstract')"
                :inactive-text="t.t('setting.menuLayoutDefault')"></el-switch></el-descriptions-item>
        <el-descriptions-item :label="t.t('setting.menuHeight')">
            <el-slider v-model="local.menu_height" size="small" :min="20" :max="60"
                style="width: 100px; display: inline-block; height: 9px"></el-slider>
        </el-descriptions-item>
        <el-descriptions-item :label="t.t('setting.menuFontSize')"><el-input-number v-model="local.menu_font_size"
                size="small" :min="10" /></el-descriptions-item>
        <el-descriptions-item :label="$t('setting.notificationDuration')"><el-tooltip>
                <template #content>
                    <div v-html="$t('setting.notificationDurationTooltip')"/>
                </template>
                <el-input-number v-model="local.notification_duration" size="small" :min="0" :step="1000" />
            </el-tooltip></el-descriptions-item>
        <el-descriptions-item :label="$t('setting.newUserGuide')"><el-tooltip>
            <template #content>
                <div v-html="$t('setting.newUserGuideTooltip')"/>
            </template>
            <el-switch v-model="local.tooltip_show"></el-switch>
        </el-tooltip>
        </el-descriptions-item>
    </el-descriptions>
    <el-descriptions v-if="false && store.login_status == LoginStatus.IsLogin" title="个人信息" :column="3">
        <el-descriptions-item label="用户id">{{ store.user.id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ store.user.username }}</el-descriptions-item>
        <el-descriptions-item :label="$t('common.prop.realName')">{{ store.user.realname }}</el-descriptions-item>
        <el-descriptions-item label="英文姓">{{ $t('common.toDo') }}</el-descriptions-item>
        <el-descriptions-item label="英文名">{{ $t('common.toDo') }}</el-descriptions-item>
        <el-descriptions-item :label="$t('common.prop.sex')">{{ $t('common.toDo') }}</el-descriptions-item>
        <el-descriptions-item label="属地">{{ $t('common.toDo') }}</el-descriptions-item>
        <el-descriptions-item label="出生年份">{{ $t('common.toDo') }}</el-descriptions-item>
    </el-descriptions>
    <el-descriptions v-if="store.login_status == LoginStatus.IsLogin" :title="$t('identifierManager.title')"></el-descriptions>
    <IdentifierManager v-if="store.login_status == LoginStatus.IsLogin"/>
    <el-descriptions v-if="false && store.login_status == LoginStatus.IsLogin" title="账号关联">
        <el-table>

        </el-table>
    </el-descriptions>
</template>

<script lang="ts" setup name="UserSettings">

import { useLocalStore, useUserStore } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import { useI18n } from 'vue-i18n';
const store = useUserStore()
const local = useLocalStore()
const t = useI18n()

import DarkMode from '@/components/widgets/DarkMode.vue'
import IdentifierManager from '@/components/widgets/IdentifierManager.vue';

</script>