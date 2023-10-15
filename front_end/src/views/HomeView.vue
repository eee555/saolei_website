<template>
  <div>
    <el-container>
      <el-main style="background-color: white;padding: 1%;">
        <el-tabs type="border-card" style=" min-height: 300px;">
          <el-tab-pane label="雷界快讯">
            2023年2月26日 11:45 周炎亮 将高级标准模式时间记录刷新为 91.52 ↑3.60</el-tab-pane>
        </el-tabs>
        <el-tabs type="border-card" style="margin-top: 2%; min-height: 300px;">
          <el-tab-pane label="最新录像">
            2023年2月26日 11:45 【业余】 周炎亮 将高级时间记录刷新为 91.52 ↑3.60</el-tab-pane>
          <el-tab-pane label="审核队列">
            <!-- <div v-for="(video, key) in review_queue" style="margin-top: 10px;">
              <span>{{ (video as any).time }}</span>
              <span>{{ (video as any).player }}</span>
            </div> -->
            <VideoList :videos="review_queue"></VideoList>
          </el-tab-pane>
        </el-tabs>
      </el-main>
      <el-aside width="30%" style="background-color: white;padding: 1%;">
        <el-tabs type="border-card">
          <el-tab-pane label="每日一星">每日一星</el-tab-pane>
          <el-tab-pane label="站长统计">站长统计</el-tab-pane>
          <el-tab-pane label="如何评选？">如何评选？</el-tab-pane>
        </el-tabs>
      </el-aside>
    </el-container>
  </div>
</template>

<script setup lang='ts'>
import { onMounted, ref, Ref, defineEmits } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import PreviewDownload from '@/components/PreviewDownload.vue';
import VideoList from '@/components/VideoList.vue';
const { proxy } = useCurrentInstance();

const review_queue = ref<any[]>([]);

onMounted(() => {
  proxy.$axios.get('/video/review_queue/',
    {
      params: {}
    }
  ).then(function (response) {
    // let review_queue_array = [];
    for (let key in response.data) {
      response.data[key] = JSON.parse(response.data[key] as string);
      response.data[key]["key"] = Number.parseInt(key);
      review_queue.value.push(response.data[key]);
    }
    // console.log(review_queue_array);
    
    // review_queue.value = review_queue_array;
  })
})
</script>

<style scope lang='less'></style>
