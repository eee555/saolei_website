<template>
    <div>
        
    </div>
</template>


<script setup lang='ts'>
// 参考：https://www.wst.tv/rankings?
// 现役排名：世界排名（累计衰减）、赛季排名（一年）、
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
    if (i == "timems") {
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
