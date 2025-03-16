<template>
    <ActivityCalendarAbstract />
    <el-divider />
    <ExperimentalFeature>
        <base-card-normal>
            <el-scrollbar>
                <BBBvSummary level="b" header />
                <el-divider />
                <BBBvSummary level="i" />
                <el-divider />
                <BBBvSummary level="e" />
            </el-scrollbar>
        </base-card-normal>
        <el-divider />
    </ExperimentalFeature>
    <el-text tag="b" size="large">
        {{ t('accountlink.title') }}
    </el-text>
    <AccountLinkManager />
    <el-divider />
    <el-badge is-dot :hidden="true && !store.new_identifier">
        <el-descriptions 
            v-if="store.login_status == LoginStatus.IsLogin"
            :title="t('identifierManager.title')"
        />
    </el-badge>
    <IdentifierManager v-if="store.login_status == LoginStatus.IsLogin" />
</template>

<script setup lang="ts">
import { ElBadge, ElDivider, ElDescriptions, ElText, ElScrollbar } from 'element-plus';
import AccountLinkManager from '@/components/AccountLinkManager.vue';
import IdentifierManager from '@/components/widgets/IdentifierManager.vue';
import { LoginStatus } from '@/utils/common/structInterface';
import { store } from '@/store';
import { useI18n } from 'vue-i18n';
import ActivityCalendarAbstract from '@/components/visualization/ActivityCalendarAbstract/App.vue';
import ExperimentalFeature from '@/components/ExperimentalFeature.vue';
import BBBvSummary from '@/components/visualization/BBBvSummary/App.vue';
import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
const { t } = useI18n();
</script>