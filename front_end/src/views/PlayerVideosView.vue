<template>
    <UserArbiterCSV :id="store.player.id" />
    <MultiSelector v-model="VideoListConfig.profile" :options="ColumnChoices" />
    <VideoList :videos="store.player.videos" :columns="VideoListConfig.profile" sortable />
</template>

<script lang="ts" setup>
// 个人主页的个人所有录像部分
import VideoList from '@/components/VideoList/App.vue';
import { store, VideoListConfig } from '../store';
import UserArbiterCSV from '@/components/widgets/UserArbiterCSV.vue';
import MultiSelector from '@/components/widgets/MultiSelector.vue';
import { ColumnChoices } from '@/utils/ms_const';

</script>
