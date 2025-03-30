<!-- 未使用 -->
<template>
    <div />
</template>


<script setup lang='ts'>
// 参考：https://www.wst.tv/rankings?
// 现役排名：世界排名（累计衰减）、赛季排名（一年）、最新比赛排名
import { onMounted, ref } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();

const review_queue = ref<any[]>([]);
const newest_queue = ref<any[]>([]);
const news_queue = ref<any[]>([]);

onMounted(() => {
    proxy.$axios.get('/video/review_queue/',
        {
            params: {},
        },
    ).then(function (response) {
        for (const key in response.data) {
            response.data[key] = JSON.parse(response.data[key] as string);
            response.data[key]["key"] = Number.parseInt(key);
            review_queue.value.push(response.data[key]);
        }
    })
    proxy.$axios.get('/video/newest_queue/',
        {
            params: {},
        },
    ).then(function (response) {
        for (const key in response.data) {
            response.data[key] = JSON.parse(response.data[key] as string);
            response.data[key]["key"] = Number.parseInt(key);
            newest_queue.value.push(response.data[key]);
        }
    })
    proxy.$axios.get('/video/news_queue/',
        {
            params: {},
        },
    ).then(function (response) {
        news_queue.value = response.data.map((v: string) => { return JSON.parse(v) })
    })
})

</script>

<style scope lang='less'>
.bottom_tabs{
    height: 500px;
    overflow: auto;

}

</style>
