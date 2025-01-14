<template>
    <ActivityCalendarAbstract />
    <el-divider />
    <ExperimentalFeature>
        <!-- <ActivityScatter2D />
        <el-divider />
        <MS3bvPB />
        <el-divider /> -->
    </ExperimentalFeature>
    <el-text tag="b" size="large">{{ t('accountlink.title') }}</el-text>
    <AccountLinkManager />
    <el-divider />
    <el-badge is-dot :hidden="true && !store.new_identifier">
        <el-descriptions v-if="store.login_status == LoginStatus.IsLogin"
            :title="t('identifierManager.title')"></el-descriptions>
    </el-badge>
    <IdentifierManager v-if="store.login_status == LoginStatus.IsLogin" />
</template>

<script setup lang="ts">
import AccountLinkManager from '@/components/AccountLinkManager.vue';
import IdentifierManager from '@/components/widgets/IdentifierManager.vue';
import { LoginStatus } from '@/utils/common/structInterface';
import { store } from '@/store';
import { useI18n } from 'vue-i18n';
import ActivityCalendarAbstract from '@/components/visualization/ActivityCalendarAbstract.vue';
import ActivityScatter2D from '@/components/visualization/ActivityScatter2D.vue';
import ExperimentalFeature from '@/components/ExperimentalFeature.vue';
import MS3bvPB from '@/components/visualization/MS3bvPB.vue';
const { t } = useI18n();
</script>