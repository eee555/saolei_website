<template>
    <el-table :data="videos_trans" :show-header="false" style="width: 100%; color: black;font-size: 16px;">
        <el-table-column prop="time" min-width="200" />
        <el-table-column prop="player" min-width="80" />
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
// 复制、生成二维码的按钮，显示结果的文本框

import { ref, watch, computed } from 'vue'
import PreviewDownload from '@/components/PreviewDownload.vue';




const data = defineProps({
    videos: {
        type: Array,
        default: []
    }
})

const videos_trans = computed(() => {
    data.videos.forEach((v: any) => {
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
            v.mode = "标准盲扫";
        }
    })
    return data.videos;
})

console.log(videos_trans);


</script>
<style></style>
  