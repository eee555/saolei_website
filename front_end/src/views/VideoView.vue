<template>
    <el-row class="mb-4" style="margin-bottom: 10px;">
        <el-button v-for="(tag, key) in level_tags" type="warning" :plain="!(level_tag_selected == key)" :size="'small'"
            @click="level_tag_selected = key as string; get_video_rank(1);">{{ tag.name }}</el-button>
    </el-row>

    <el-row class="mb-4" style="margin-bottom: 10px;">
        <el-button v-for="(tag, key) in mode_tags" type="success" :plain="!(mode_tag_selected == key)" :size="'small'"
            @click="mode_tag_selected = key as string; get_video_rank(1);">{{ tag.name }}</el-button>
    </el-row>

    <el-row class="mb-4" style="margin-bottom: 10px;">
        <el-button v-for="(tag, key) in index_tags" type="primary" :plain="!(index_tag_selected == key)" :size="'small'"
            @click="index_tag_selected = key as string; mod_style(); get_video_rank(1);">{{ tag.name
            }}</el-button>
    </el-row>

    <div style="width: 80%;font-size:20px;margin: auto;margin-top: 10px;">
        <div style="border-bottom: 1px solid #555;padding-bottom: 10px;">
            <div class="rank">排名</div>
            <span class="utime">上传时间</span>
            <span class="name">姓名</span>
            <span class="bbbv">3BV</span>
            <span class="bbbvs">3BV/s</span>
            <span class="rtime">成绩</span>
            <span v-show="index_visible" class="index">{{ index_tag_selected }}</span>
            <span class="operation">操作</span>
        </div>
        <div v-for="(video, key) in videoData" style="margin-top: 10px;">
            <div class="rank">{{ key - 19 + (state.CurrentPage) * 20 }}</div>

            <span v-if="'upload_time' in video" class="utime">{{ video.upload_time }}</span>
            <span v-else class="utime">{{ video.video__upload_time }}</span>

            <span v-if="'player__realname' in video" class="name">{{ video.player__realname }}</span>
            <span v-else class="name">{{ video.video__player__realname }}</span>

            <span v-if="'bv' in video" class="bbbv">{{ video.bv }}</span>
            <span v-else class="bbbv">{{ video.video__bv }}</span>

            <span v-if="'bvs' in video" class="bbbvs">{{ to_fixed_n(video.bvs, 3) }}</span>
            <span v-else class="bbbvs">{{ to_fixed_n(video.video__bvs, 3) }}</span>

            <span v-if="'rtime' in video" class="rtime">{{ to_fixed_n(video.rtime, 3) }}</span>
            <span v-else class="rtime">{{ to_fixed_n(video.video__rtime, 3) }}</span>

            <span v-show="index_visible" class="index">{{
                to_fixed_n(video["video__" + index_tags[index_tag_selected].key],
                    index_tags[index_tag_selected].to_fixed) }}</span>
            <span class="operation">
                <PreviewDownload :id="video.id"></PreviewDownload>
            </span>
        </div>
    </div>

    <div style="margin-top: 16px;">
        <el-pagination v-model:current-page="state.CurrentPage" @current-change="currentChange" @prev-click="prevClick"
            :next-click="nextClick" :page-size="20" layout="prev, pager, next, jumper" :page-count="state.Total"
            prev-text="上一页" next-text="下一页">
        </el-pagination>
    </div>
</template>
  
<script lang="ts" setup>
// 全网录像的检索器，根据三个维度排序
import { onMounted, ref, Ref, defineEmits, reactive } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import PreviewDownload from '@/components/PreviewDownload.vue';
const { proxy } = useCurrentInstance();

const level_tag_selected = ref("EXPERT");
const mode_tag_selected = ref("STD");
const index_tag_selected = ref("rtime");

const index_visible = ref(true);

const state = reactive({
    tableLoading: false,
    CurrentPage: 1,
    // PageSize: 20,
    Total: 3,
});

// const test  = reactive({v: 5});
const videoData = reactive<Video[]>([]);
interface Video {
    id: number;
    upload_time?: string;
    player__realname?: string;
    bv?: number;
    bvs?: number;
    rtime?: number;
    video__upload_time?: string;
    video__player__realname?: string;
    video__bv?: number;
    video__bvs?: number;
    video__rtime?: number;
    index?: number;
    [index: string]: string | number | undefined;
}

interface NameKey {
    [index: string]: string;
}
interface Tags {
    [index: string]: NameKey;
}
interface NameKeyReverse {
    name: string;
    key: string;
    reverse: boolean;
    to_fixed: number;
}
interface TagsReverse {
    [index: string]: NameKeyReverse;
}

const level_tags: Tags = {
    "BEGINNER": { name: "初级", key: "b" },
    "INTERMEDIATE": { name: "中级", key: "i" },
    "EXPERT": { name: "高级", key: "e" }
};

const mode_tags: Tags = {
    "STD": { name: "标准", key: "00" },
    "NF": { name: "盲扫", key: "12" },
    "UPK": { name: "UPK", key: "01" },
    "WQI": { name: "Win7", key: "04" },
    "JSW": { name: "竞速无猜", key: "05" },
    "QWC": { name: "强无猜", key: "06" },
    "RWC": { name: "弱无猜", key: "07" },
    "ZWC": { name: "准无猜", key: "08" },
    "QKC": { name: "强可猜", key: "09" },
    "RKC": { name: "弱可猜", key: "10" },
    "BZD": { name: "递归", key: "11" }
}


// reverse: true从小到大
const index_tags: TagsReverse = {
    "upload_time": { name: "上传时间", key: "upload_time", reverse: true, to_fixed: -1 },
    "rtime": { name: "成绩", key: "rtime", reverse: false, to_fixed: 3 },
    "bbbv": { name: "3BV", key: "bv", reverse: false, to_fixed: 0 },
    "bbbv_s": { name: "3BV/s", key: "bvs", reverse: true, to_fixed: 3 },
    "left_s": { name: "left/s", key: "left_s", reverse: true, to_fixed: 3 },
    "right_s": { name: "right/s", key: "right_s", reverse: true, to_fixed: 3 },
    "double_s": { name: "double/s", key: "double_s", reverse: true, to_fixed: 3 },
    "cl_s": { name: "cl/s", key: "cl_s", reverse: true, to_fixed: 3 },
    "path": { name: "path", key: "path", reverse: false, to_fixed: 2 },
    "stnb": { name: "STNB", key: "stnb", reverse: true, to_fixed: 2 },
    "ioe": { name: "IOE", key: "ioe", reverse: true, to_fixed: 3 },
    "thrp": { name: "ThrP", key: "thrp", reverse: true, to_fixed: 3 },
    "ce_s": { name: "ce/s", key: "ce_s", reverse: true, to_fixed: 3 },
    "op": { name: "空", key: "op", reverse: false, to_fixed: 0 },
    "is": { name: "岛", key: "isl", reverse: false, to_fixed: 0 },
    "cell1": { name: "1", key: "cell1", reverse: false, to_fixed: 0 },
    "cell2": { name: "2", key: "cell2", reverse: false, to_fixed: 0 },
    "cell3": { name: "3", key: "cell3", reverse: false, to_fixed: 0 },
    "cell4": { name: "4", key: "cell4", reverse: false, to_fixed: 0 },
    "cell5": { name: "5", key: "cell5", reverse: false, to_fixed: 0 },
    "cell6": { name: "6", key: "cell6", reverse: false, to_fixed: 0 },
    "cell7": { name: "7", key: "cell7", reverse: false, to_fixed: 0 },
    "cell8": { name: "8", key: "cell8", reverse: false, to_fixed: 0 }
}

onMounted(() => {
    document.getElementsByClassName("el-pagination__goto")[0].childNodes[0].nodeValue = "转到";
    // 把分页器的go to改成中文。


    mod_style();
    get_video_rank(1);
})

function to_fixed_n(input: string | number | undefined, to_fixed: number): string | number | undefined {
    // 返回保留to_fixed位小数的字符串，四舍六入五取双
    if (input === undefined) {
        return input;
    }
    if (to_fixed <= 0) {
        return input;
    }
    if (typeof (input) == "string") {
        return parseFloat(input).toFixed(to_fixed);
    }
    return (input as number).toFixed(to_fixed);
}

const mod_style = () => {
    // 调整列宽样式
    // console.log(index_visible.value);

    index_visible.value = !["upload_time", "bbbv", "bbbv_s", "rtime"].
        includes(index_tag_selected.value);
}

const get_video_rank = (page: number) => {
    state.CurrentPage = page
    let index = index_tags[index_tag_selected.value].key;
    if (index_tags[index_tag_selected.value].reverse) {
        index = "-" + index; // 适配django
    }
    proxy.$axios.get('/video/query/',
        {
            params: {
                level: level_tags[level_tag_selected.value].key,
                mode: mode_tags[mode_tag_selected.value].key,
                index: index,
                page: page,
            }
        }
    ).then(function (response) {
        const data = JSON.parse(response.data);
        if ((data.videos).length >= 0) {
            videoData.splice(0, videoData.length);
            videoData.push(...data.videos);
            state.Total = data.total_page;
            console.log(videoData);
            // console.log(315);
            
            // console.log(index_tag_selected);


        } else {
            // console.log("000");
        }
    })
}

const currentChange = (val: number) => {
    state.CurrentPage = Math.ceil(val);
    get_video_rank(state.CurrentPage);
}
const prevClick = () => {
    state.CurrentPage = state.CurrentPage - 1;
    if (state.CurrentPage < 1) {
        state.CurrentPage = 1;
    }
    get_video_rank(state.CurrentPage);
}
const nextClick = () => {
    state.CurrentPage = state.CurrentPage + 1;
    if (state.CurrentPage > state.Total) {
        state.CurrentPage = state.Total;
    }
    get_video_rank(state.CurrentPage);
}



</script>


<style lang="less" scoped>
.rank {
    width: 5%;
    display: inline-block;
}

.utime {
    width: 20%;
    display: inline-block;
    text-align: center;
}

.name {
    width: 16%;
    display: inline-block;
    text-align: center;
}

.bbbv {
    width: 8%;
    display: inline-block;
    text-align: center;
}

.bbbvs {
    width: 10%;
    display: inline-block;
    text-align: center;
}

.rtime {
    width: 10%;
    display: inline-block;
    text-align: center;
}

.index {
    width: 10%;
    display: inline-block;
}

.operation {
    width: 20%;
    display: inline-block;
    text-align: center;
}

.el-pagination {
    justify-content: center;
}
</style>









