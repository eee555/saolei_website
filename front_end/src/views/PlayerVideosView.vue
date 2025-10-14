<template>
    <el-row>
        <UserArbiterCSV :id="store.player.id" />
        <span style="flex: 1" />
        <el-button circle :type="showSetting ? 'primary' : 'default'" @click="showSetting = !showSetting">
            <base-icon-setting />
        </el-button>
    </el-row>
    <MultiSelector v-if="showSetting" v-model="VideoListConfig.profile" :options="ColumnChoices" />
    <VideoList :videos="store.player.videos" :columns="VideoListConfig.profile" sortable />
</template>

<script lang="ts" setup>
// 个人主页的个人所有录像部分
import VideoList from '@/components/VideoList/App.vue';
import { store, VideoListConfig } from '../store';
import UserArbiterCSV from '@/components/widgets/UserArbiterCSV.vue';
import MultiSelector from '@/components/widgets/MultiSelector.vue';
import { ColumnChoices } from '@/utils/ms_const';
import BaseIconSetting from '@/components/common/BaseIconSetting.vue';
import { ref } from 'vue';
import { ElButton, ElRow } from 'element-plus';

const showSetting = ref(false);

</script>
