<template>
    <ActivityCalendarAbstract />
    <el-divider/>
    <el-text tag="b" size="large">{{ t('accountlink.title') }}</el-text>
    <AccountLinkManager />
    <el-divider/>
    <el-badge is-dot :hidden="true && !store.new_identifier">
        <el-descriptions v-if="store.login_status == LoginStatus.IsLogin" :title="t('identifierManager.title')"></el-descriptions>
    </el-badge>
    <IdentifierManager v-if="store.login_status == LoginStatus.IsLogin"/>
</template>

<script setup lang="ts">
import AccountLinkManager from '@/components/AccountLinkManager.vue';
import IdentifierManager from '@/components/widgets/IdentifierManager.vue';
import { LoginStatus } from '@/utils/common/structInterface';
import { store } from '@/store';
import { useI18n } from 'vue-i18n';
import ActivityCalendarAbstract from '@/components/visualization/ActivityCalendarAbstract.vue';
const { t } = useI18n();
</script>