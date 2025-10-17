<template>
    <el-row>
        <UserArbiterCSV :id="store.player.id" />
        <span style="flex: 1" />
        <el-button circle :type="showSetting ? 'primary' : 'default'" @click="showSetting = !showSetting">
            <base-icon-setting />
        </el-button>
    </el-row>
    <MultiSelector v-if="showSetting" v-model="VideoListConfig.profile" :options="thisColumnChoices" :labels="thisColumnChoices.map((s) => t(`common.prop.${s}`))" />
    <VideoList :videos="store.player.videos" :columns="VideoListConfig.profile" sortable />
</template>

<script lang="ts" setup>
// 个人主页的个人所有录像部分
import VideoList from '@/components/VideoList/App.vue';
import { store, VideoListConfig } from '../store';
import UserArbiterCSV from '@/components/widgets/UserArbiterCSV.vue';
import MultiSelector from '@/components/widgets/MultiSelector.vue';
import BaseIconSetting from '@/components/common/BaseIconSetting.vue';
import { ref } from 'vue';
import { ElButton, ElRow } from 'element-plus';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const showSetting = ref(false);
const thisColumnChoices = ['bv', 'bvs', 'stnb', 'ces', 'cls', 'corr', 'end_time', 'ioe', 'level', 'state', 'software', 'thrp', 'time', 'upload_time', 'path', 'file_size', 'mode'] as const;

</script>
