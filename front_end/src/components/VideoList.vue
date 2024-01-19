<template>
    <el-table :data="videos_trans" :show-header="false" style="width: 100%; color: black;font-size: 16px;">
        <el-table-column prop="time" min-width="200" />
        <el-table-column v-if="need_player_name" min-width="80">
            <template #default="player">
                <PlayerName class="name" :user_id="+player.row.player_id" :user_name="player.row.player"></PlayerName>
            </template>
        </el-table-column>
        <el-table-column v-else prop="player" min-width="80" />
        <el-table-column prop="level" min-width="80" />
        <el-table-column prop="mode" min-width="80" />
        <el-table-column prop="rtime" min-width="90" />
        <el-table-column prop="bv" min-width="60" />
        <el-table-column min-width="200">
            <template #default="scope">
                <PreviewDownload :id="scope.row.key"></PreviewDownload>
            </template>
        </el-table-column>
    </el-table>
</template>
  
<script setup lang="ts">
// 录像列表的组件

import { ref, watch, computed } from 'vue'
import PreviewDownload from '@/components/PreviewDownload.vue';
import {utc_to_local_format} from "@/utils/system/tools";
import PlayerName from '@/components/PlayerName.vue';

const data = defineProps({
    videos: {
        type: Array,
        default: []
    },
    // 反序
    reverse: {
        type: Boolean,
        default: false
    },
    // 需要用可以点开摘要的用户组件
    need_player_name: {
        type: Boolean,
        default: true
    }
})

const videos_trans = computed(() => {
    data.videos.forEach((v: any) => {
        v.time = utc_to_local_format(v.time);
        if (v.level == "b") {
            v.level = "初级";
        } else if (v.level == "i") {
            v.level = "中级";
        } else if (v.level == "e") {
            v.level = "高级";
        }
        v.rtime +="s";
        if (v.mode == "00") {
            v.mode = "标准";
        } else if (v.mode == "01") {
            v.mode = "UPK";
        } else if (v.mode == "04") {
            v.mode = "Win7";
        } else if (v.mode == "05") {
            v.mode = "竞速无猜";
        } else if (v.mode == "06") {
            v.mode = "强无猜";
        } else if (v.mode == "07") {
            v.mode = "弱无猜";
        } else if (v.mode == "08") {
            v.mode = "准无猜";
        } else if (v.mode == "09") {
            v.mode = "强可猜";
        } else if (v.mode == "10") {
            v.mode = "弱可猜";
        } else if (v.mode == "11") {
            v.mode = "递归";
        } else if (v.mode == "12") {
            v.mode = "标准NF";
        }
    })
    if(data.reverse){
        data.videos.reverse();
    }
    return data.videos;
})

// console.log(videos_trans);


</script>
<style></style>
  