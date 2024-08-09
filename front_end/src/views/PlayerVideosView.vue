<template>
    <el-card class="box-card" body-style="" style="max-height: 800px; overflow: auto;">
        <el-skeleton animated v-show="loading" :rows="8" />
        <VideoList :videos="videos_queue" :need_player_name="false"></VideoList>
    </el-card>
</template>

<script lang="ts" setup>
// 个人主页的个人所有录像部分
import { onMounted, ref, Ref } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
// import { genFileId, ElMessage } from 'element-plus'
import { Record } from "@/utils/common/structInterface";
import VideoList from '@/components/VideoList.vue';
// import { fa } from 'element-plus/es/locale';
import { useUserStore } from '../store'
const store = useUserStore()

const loading = ref(true)

const videos_queue = ref<any[]>([]);


onMounted(() => {
    // const player = proxy.$store.state.player;
    // const player = JSON.parse(localStorage.getItem("player") as string);
    const player = store.player;
    proxy.$axios.get('/video/query_by_id/',
        {
            params: { id: player.id }
        }
    ).then(function (response) {
        let videos = response.data;
        console.log(videos)
        for (let key in videos) {
            videos[key].key = videos[key].id;
            videos_queue.value.push(videos[key]);
        }
        loading.value = false;

    })
})

</script>


<style>
.avatar-uploader {
    margin: auto;
    text-align: center;
    margin-top: 30px;

}
</style>
