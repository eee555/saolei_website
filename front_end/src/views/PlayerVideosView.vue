<template>
    <el-card class="box-card" body-style="" style="max-height: 800px; overflow: auto;">
        <el-skeleton animated v-show="loading" :rows="8" />
        <VideoList :videos="videos_queue"></VideoList>
    </el-card>
</template>
  
<script lang="ts" setup>
// 个人主页的个人所有录像部分
import { onMounted, ref, Ref, defineEmits } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
import { genFileId, ElMessage } from 'element-plus'
import { Record, RecordBIE } from "@/utils/common/structInterface";
import VideoList from '@/components/VideoList.vue';

const loading = ref(true)

const videos_queue = ref<any[]>([]);


onMounted(() => {
    const player = proxy.$store.state.player;
    proxy.$axios.get('/video/query_by_id/',
        {
            params: {id: player.id}
        }
    ).then(function (response) {
        let videos = JSON.parse(response.data as string).videos;
        console.log(videos);
        
        for (let key in videos) {
            videos[key].key = videos[key].id;
            videos[key].time = videos[key].upload_time;
            videos[key].player = player.realname;
            videos_queue.value.push(videos[key]);
        }
        console.log(videos_queue.value);
        loading.value = false;
        
    })
})

// 把记录数据转一下嵌套的结构，做数据格式的适配
function trans_record(r: RecordBIE): Record[] {
    const record: Record[] = [];
    for (let i = 0; i < r.time.length; i++) {
        record.push({
            time: r.time[i],
            bvs: r.bvs[i],
            stnb: r.stnb[i],
            ioe: r.ioe[i],
            path: r.path[i],
            time_id: r.time_id[i],
            bvs_id: r.bvs_id[i],
            stnb_id: r.stnb_id[i],
            ioe_id: r.ioe_id[i],
            path_id: r.path_id[i],
        })
    }
    return record;
}








</script>


<style>
.avatar-uploader {
    margin: auto;
    text-align: center;
    margin-top: 30px;

}
</style>









