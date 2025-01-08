<template>
    <!-- 此处6-13行暂时屏蔽。vue3使用echarts时，vite命令的调试环境没有问题，但
     vite build出来的打包结果会报isFunction is not a function，结果不能进入个人主页，
     就不能上传录像。修改vite版本4、5、6都没用。但是，这并不意味着只要用echarts就会报错，
     因为日历图刚做出时使用时候没问题，可能是需要满足某些条件。目前来说，解除其中任何一行都会报错。 -->
    <!-- <ActivityCalendarAbstract />
    <el-divider />
    <ExperimentalFeature>
        <ActivityScatter2D />
        <el-divider />
        <MS3bvPB />
        <el-divider />
    </ExperimentalFeature> -->
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