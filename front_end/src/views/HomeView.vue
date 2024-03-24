<template>
    <div>
        <el-container>
            <el-main style="background-color: white;padding: 1%;">
                <el-tabs type="border-card" style=" min-height: 300px;">
                    <el-tab-pane label="雷界快讯" style="max-height: 300px; overflow: auto;">
                        <div v-for="news in news_queue">
                            {{ utc_to_local_format(news.time) }}<PlayerName class="name" :user_id="+news.player_id" :user_name="news.player">
                            </PlayerName>将{{ trans_mode(news.mode) }}模式{{ trans_level(news.level)
                            }}{{ trans_index(news.index) }}记录刷新为
                            <PreviewNumber :id="news.video_id" :text="to_fixed_n(news.value, 3)"></PreviewNumber>
                            {{ news.delta > 0 ? "↑" : "↓" }}{{ news.delta }}

                        </div>
                        <!-- 2023年2月26日 11:45 周炎亮 将高级标准模式时间记录刷新为 91.52 ↑3.60-->
                    </el-tab-pane>
                </el-tabs>
                <el-tabs type="border-card" style="margin-top: 2%;">
                    <el-tab-pane label="最新录像" class="bottom_tabs" :lazy="true">
                        <VideoList :videos="newest_queue" :reverse="true"></VideoList>
                    </el-tab-pane>
                    <el-tab-pane label="审核队列" class="bottom_tabs" :lazy="true">
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
import PreviewNumber from '@/components/PreviewNumber.vue';
import VideoList from '@/components/VideoList.vue';
import PlayerName from '@/components/PlayerName.vue';
import { to_fixed_n } from "@/utils";
const { proxy } = useCurrentInstance();
import { utc_to_local_format } from "@/utils/system/tools";

const review_queue = ref<any[]>([]);
const newest_queue = ref<any[]>([]);
const news_queue = ref<any[]>([]);

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
        for (let key in response.data) {
            response.data[key] = JSON.parse(response.data[key] as string);
            response.data[key]["key"] = Number.parseInt(key);
            newest_queue.value.push(response.data[key]);
        }
    })
    proxy.$axios.get('/video/news_queue/',
        {
            params: {}
        }
    ).then(function (response) {
        news_queue.value = response.data.map((v: string) => { return JSON.parse(v) })
    })
})

const trans_level = (l: string) => {
    if (l == "b") {
        return "初级"
    } else if (l == "i") {
        return "中级"
    } else if (l == "e") {
        return "高级"
    } else {
        return "自定义"
    }
}

const trans_mode = (m: string) => {
    if (m == "std") {
        return "标准"
    } else if (m == "nf") {
        return "盲扫"
    } else if (m == "ng") {
        return "无猜"
    } else if (m == "dg") {
        return "递归"
    } else {
        return "自定义"
    }
}

const trans_index = (i: string) => {
    if (i == "time") {
        return "时间"
    } else if (i == "bvs") {
        return "盲扫3BV/s"
    } else if (i == "path") {
        return "Path"
    } else if (i == "stnb") {
        return "STNB"
    } else if (i == "ioe") {
        return "IOE"
    } else {
        return "自定义"
    }
}

</script>

<style scope lang='less'>
.bottom_tabs{
    height: 500px;
    overflow: auto;

}

</style>
