<template>
    <UserArbiterCSV :id="store.player.id" />
    <VideoList :videos="store.player.videos" :need_player_name="false" reverse max-height="800"></VideoList>
</template>

<script lang="ts" setup>
// 个人主页的个人所有录像部分
import { ElCard } from 'element-plus';
import VideoList from '@/components/VideoList.vue';
import { store } from '../store'
import UserArbiterCSV from '@/components/widgets/UserArbiterCSV.vue';

</script>
