<template>
    <UserArbiterCSV :id="store.player.id" />
    <el-card class="box-card" body-style="" style="max-height: 800px; overflow: auto; margin-top:5px">
        <el-skeleton animated v-show="store.player.loading" :rows="8" />
        <VideoList :videos="store.player.videos" :need_player_name="false" reverse></VideoList>
    </el-card>
</template>

<script lang="ts" setup>
// 个人主页的个人所有录像部分
import VideoList from '@/components/VideoList.vue';
import { store } from '../store'
import UserArbiterCSV from '@/components/widgets/UserArbiterCSV.vue';

</script>
