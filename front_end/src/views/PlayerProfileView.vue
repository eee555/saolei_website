<template>
    <ActivityCalendarAbstract />
    <div style="height: 10px;" />
    <base-card-normal v-if="store.player.videos.length > 0">
        <BBBvSummaryHeader />
        <el-scrollbar aria-orientation="horizontal" :style="{ zoom: BBBvSummaryConfig.zoom }">
            <BBBvSummary level="b" header />
            <BBBvSummary level="i" />
            <BBBvSummary level="e" />
        </el-scrollbar>
    </base-card-normal>
    <el-divider />
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
import { BBBvSummaryConfig, store } from '@/store';
import { useI18n } from 'vue-i18n';
import ActivityCalendarAbstract from '@/components/visualization/ActivityCalendarAbstract/App.vue';
import BBBvSummary from '@/components/visualization/BBBvSummary/App.vue';
import BBBvSummaryHeader from '@/components/visualization/BBBvSummary/Header.vue';
import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
const { t } = useI18n();
</script>
