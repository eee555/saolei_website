<template>
    <el-row>
        <UserArbiterCSV :id="user.id" />
        <span style="flex: 1" />
        <el-button circle :type="showSetting ? 'primary' : 'default'" @click="showSetting = !showSetting">
            <base-icon-setting />
        </el-button>
    </el-row>
    <MultiSelector v-if="showSetting" v-model="VideoListConfig.profile" :options="thisColumnChoices" :labels="thisColumnChoices.map((s) => t(`common.prop.${s}`))" />
    <VideoList :videos="user.videos" :columns="VideoListConfig.profile" sortable paginator />
</template>

<script lang="ts" setup>
// 个人主页的个人所有录像部分
import { ElButton, ElRow } from 'element-plus';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';


import { BaseIconSetting } from '@/components/common/icon';
import VideoList from '@/components/VideoList/App.vue';
import MultiSelector from '@/components/widgets/MultiSelector.vue';
import UserArbiterCSV from '@/components/widgets/UserArbiterCSV.vue';
import { VideoListConfig } from '@/store';
import { ArrayUtils } from '@/utils/arrays';
import { ColumnChoices } from '@/utils/ms_const';
import { UserProfile } from '@/utils/userprofile';

const { t } = useI18n();

const user = defineModel('user', { type: UserProfile, required: true });

const showSetting = ref(false);
const thisColumnChoices = ArrayUtils.sortByReferenceOrder(['bv', 'bvs', 'stnb', 'ces', 'cls', 'corr', 'end_time', 'ioe', 'level', 'state', 'software', 'thrp', 'time', 'upload_time', 'path', 'file_size', 'mode'], ColumnChoices);

</script>
