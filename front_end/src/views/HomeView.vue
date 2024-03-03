<template>
  <div>
    <el-container>
      <el-main style="background-color: white;padding: 1%;">
        <el-tabs type="border-card" style=" min-height: 300px;">
          <el-tab-pane label="雷界快讯" style="max-height: 300px; overflow: auto;">
            2023年2月26日 11:45 周炎亮 将高级标准模式时间记录刷新为 91.52 ↑3.60</el-tab-pane>
        </el-tabs>
        <el-tabs type="border-card" style="margin-top: 2%; min-height: 300px;">
          <el-tab-pane label="最新录像" style="max-height: 800px; overflow: auto;" :lazy="true">
            <VideoList :videos="newest_queue" :reverse="true"></VideoList>
          </el-tab-pane>
          <el-tab-pane label="审核队列" :lazy="true">
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
import { onMounted, ref, Ref } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import PreviewDownload from '@/components/PreviewDownload.vue';
import VideoList from '@/components/VideoList.vue';
const { proxy } = useCurrentInstance();

const review_queue = ref<any[]>([]);
const newest_queue = ref<any[]>([]);

onMounted(() => {
  proxy.$axios.get('/video/review_queue/',
    {
      params: {}
    }
  ).then(function (response) {
    for (let key in response.data) {
      response.data[key] = JSON.parse(response.data[key] as string);
      response.data[key]["key"] = Number.parseInt(key);
      review_queue.value.push(response.data[key]);
    }
  })
  proxy.$axios.get('/video/newest_queue/',
    {
      params: {}
    }
  ).then(function (response) {
    // console.log(response.data);
    
    for (let key in response.data) {
      response.data[key] = JSON.parse(response.data[key] as string);
      response.data[key]["key"] = Number.parseInt(key);
      newest_queue.value.push(response.data[key]);
    }
    // console.log(newest_queue.value);
  })
})
</script>

<style scope lang='less'></style>
