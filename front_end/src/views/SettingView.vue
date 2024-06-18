<template>
    <el-descriptions title="通用设置">
        <el-descriptions-item label="语言切换"><el-switch v-model="local.language_show" :active-text="$t('common.show')"
                :inactive-text="$t('common.hide')"></el-switch></el-descriptions-item>
        <el-descriptions-item label="菜单排版"><el-switch v-model="local.menu_icon" active-text="抽象"
                inactive-text="默认"></el-switch></el-descriptions-item>
    </el-descriptions>
    <el-descriptions v-if="store.login_status == LoginStatus.IsLogin" title="个人信息">
        <el-descriptions-item label="用户id">{{ store.user.id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ store.user.username }}</el-descriptions-item>
        <el-descriptions-item :label="$t('common.prop.realName')">{{ store.user.realname }}</el-descriptions-item>
        <el-descriptions-item label="英文姓">{{ $t('common.toDo') }}</el-descriptions-item>
        <el-descriptions-item label="英文名">{{ $t('common.toDo') }}</el-descriptions-item>
        <el-descriptions-item :label="$t('common.prop.sex')">{{ $t('common.toDo') }}</el-descriptions-item>
        <el-descriptions-item label="属地">{{ $t('common.toDo') }}</el-descriptions-item>
        <el-descriptions-item label="出生年份">{{ $t('common.toDo') }}</el-descriptions-item>
    </el-descriptions>
    <el-descriptions v-if="store.login_status == LoginStatus.IsLogin" title="账号关联">
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

</script>