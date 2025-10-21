<template>
    <ActivityCalendarAbstract :video-list="store.player.videos" :options="activityCalendarConfig" :dark-mode="local.darkmode" />
    <div style="height: 10px;" />
    <base-card-normal v-if="store.player.videos.length > 0">
        <BBBvSummaryHeader />
        <el-scrollbar aria-orientation="horizontal" :style="{ zoom: BBBvSummaryConfig.zoom }">
            <BBBvSummary level="b" header :video-list="store.player.videos" />
            <BBBvSummary level="i" :video-list="store.player.videos" />
            <BBBvSummary level="e" :video-list="store.player.videos" />
        </el-scrollbar>
    </base-card-normal>
    <el-divider />
    <el-text tag="b" size="large">
        {{ t('accountlink.title') }}
    </el-text>
    <AccountLinkManager />
    <el-divider />
    <el-text tag="b" size="large">
        {{ t('identifierManager.title') }}
    </el-text>
    &nbsp;
    <base-overlay>
        <base-icon-info />
        <template #overlay>
            <IdentifierHelper style="width: 60%; min-width: 400px; max-width: 100%; margin: auto; display: block" />
        </template>
    </base-overlay>
    <IdentifierManager />
</template>

<script setup lang="ts">
import { ElDivider, ElText, ElScrollbar } from 'element-plus';
import AccountLinkManager from '@/components/AccountLinkManager.vue';
import IdentifierManager from '@/components/widgets/IdentifierManager.vue';
import { activityCalendarConfig, BBBvSummaryConfig, local, store } from '@/store';
import { useI18n } from 'vue-i18n';
import ActivityCalendarAbstract from '@/components/visualization/ActivityCalendarAbstract/App.vue';
import BBBvSummary from '@/components/visualization/BBBvSummary/App.vue';
import BBBvSummaryHeader from '@/components/visualization/BBBvSummary/Header.vue';
import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import BaseOverlay from '@/components/common/BaseOverlay.vue';
import BaseIconInfo from '@/components/common/BaseIconInfo.vue';
import { defineAsyncComponent } from 'vue';

const { t } = useI18n();
const IdentifierHelper = defineAsyncComponent(() => import('@/components/dialogs/IdentifierHelper.vue'));
</script>
