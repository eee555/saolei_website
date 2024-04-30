<template>
    <Teleport to=".common-layout">
        <el-dialog v-model="preview_visible"
            style="background-color: rgba(240, 240, 240, 0.48); backdrop-filter: blur(1px);" draggable align-center
            destroy-on-close :modal="false" :lock-scroll="false">
            <iframe class="flop-player-iframe flop-player-display-none" style="width: 100%; height: 500px; border: 0px"
                src="/flop/index.html" ref="video_iframe"></iframe>
        </el-dialog>
    </Teleport>
    <el-row class="mb-4" style="margin-bottom: 10px;">
        <el-button v-for="(tag, key) in level_tags" type="warning" :plain="!(level_tag_selected == key)" :size="'small'"
            @click="level_tag_selected = key as string; request_videos();">{{ tag.name }}</el-button>
    </el-row>

    <el-row class="mb-4" style="margin-bottom: 10px;">
        <el-button v-for="(tag, key) in mode_tags" type="success" :plain="!(mode_tag_selected == key)" :size="'small'"
            @click="mode_tag_selected = key as string; request_videos();">{{ tag.name }}</el-button>
    </el-row>

    <el-row class="mb-4" style="margin-bottom: 10px;">
        <el-button v-for="(value, key) in index_tags" type="primary" :plain="!value.selected" :size="'small'"
            @click="index_select(key, value)">{{ value.name
            }}</el-button>
    </el-row>

    <div style="width: 80%;font-size:20px;margin: auto;margin-top: 10px;">
        <el-table :data="videoList" @sort-change="handleSortChange" @row-click="preview">
            <el-table-column type="index" :index="offsetIndex" fixed></el-table-column>
            <el-table-column v-for="key in selected_index()" 
                :prop="index_tags[key].key" 
                :label="index_tags[key].name"
                :formatter="columnFormatter(key)"
                sortable="custom"
                :sort-orders="index_tags[key].reverse ? (['descending', 'ascending']) : (['ascending', 'descending'])">
            </el-table-column>
        </el-table>
    </div>

    <div style="margin-top: 16px;">
        <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="state.CurrentPage"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="state.PageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="state.VideoCount">
        </el-pagination>
    </div>
</template>

<script lang="ts" setup>
// 全网录像的检索器，根据三个维度排序
import { onMounted, ref, Ref, reactive } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import PreviewDownload from '@/components/PreviewDownload.vue';
import PlayerName from '@/components/PlayerName.vue';
const { proxy } = useCurrentInstance();
import { utc_to_local_format } from "@/utils/system/tools";
import { ms_to_s } from "@/utils";
import { genFileId, ElMessage } from 'element-plus'

const preview_visible = ref(false);


const level_tag_selected = ref("EXPERT");
const mode_tag_selected = ref("STD");
const index_tag_selected = ref("timems");

const index_visible = ref(true);

const state = reactive({
    tableLoading: false,
    CurrentPage: 1,
    PageSize: 10,
    VideoCount: 0,
    ReverseOrder: false,
    Total: 3
});

// const test  = reactive({v: 5});
const videoData = reactive<Video[]>([]);
const videoList = reactive<Video[]>([]);
// 带下划线与不带的至少存在一个
interface Video {
    [key: string]: string | number; // Assuming all values are strings, change as needed
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
    selected: boolean;
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
const index_tags: TagsReverse = reactive({
    "upload_time": { name: "上传时间", key: "upload_time", reverse: true, to_fixed: -1, selected: true },
    "name": { name: "姓名", key: "player__realname", reverse: false, to_fixed: 0, selected: true},
    "timems": { name: "成绩", key: "timems", reverse: false, to_fixed: 3, selected: true },
    "bbbv": { name: "3BV", key: "bv", reverse: false, to_fixed: 0, selected: true },
    "bbbv_s": { name: "3BV/s", key: "bvs", reverse: true, to_fixed: 3, selected: true },
    "left_s": { name: "left/s", key: "video__left_s", reverse: true, to_fixed: 3, selected: false },
    "right_s": { name: "right/s", key: "video__right_s", reverse: true, to_fixed: 3, selected: false },
    "double_s": { name: "double/s", key: "video__double_s", reverse: true, to_fixed: 3, selected: false },
    "cl_s": { name: "cl/s", key: "video__cl_s", reverse: true, to_fixed: 3, selected: false },
    "path": { name: "path", key: "video__path", reverse: false, to_fixed: 2, selected: false },
    "stnb": { name: "STNB", key: "video__stnb", reverse: true, to_fixed: 2, selected: true },
    "ioe": { name: "IOE", key: "video__ioe", reverse: true, to_fixed: 3, selected: false },
    "thrp": { name: "ThrP", key: "video__thrp", reverse: true, to_fixed: 3, selected: false },
    "ce_s": { name: "ce/s", key: "video__ce_s", reverse: true, to_fixed: 3, selected: false },
    "op": { name: "空", key: "video__op", reverse: false, to_fixed: 0, selected: false },
    "is": { name: "岛", key: "video__isl", reverse: false, to_fixed: 0, selected: false },
    "cell1": { name: "1", key: "video__cell1", reverse: false, to_fixed: 0, selected: false },
    "cell2": { name: "2", key: "video__cell2", reverse: false, to_fixed: 0, selected: false },
    "cell3": { name: "3", key: "video__cell3", reverse: false, to_fixed: 0, selected: false },
    "cell4": { name: "4", key: "video__cell4", reverse: false, to_fixed: 0, selected: false },
    "cell5": { name: "5", key: "video__cell5", reverse: false, to_fixed: 0, selected: false },
    "cell6": { name: "6", key: "video__cell6", reverse: false, to_fixed: 0, selected: false },
    "cell7": { name: "7", key: "video__cell7", reverse: false, to_fixed: 0, selected: false },
    "cell8": { name: "8", key: "video__cell8", reverse: false, to_fixed: 0, selected: false }
})

const selected_index = () => {
    var list = [];
    for (var key of Object.keys(index_tags)) {
        if (index_tags[key].selected) {
            list.push(key);
        }
    }
    return list;
}

const columnFormatter = (key: string) => {
    if (key == "upload_time") {
        return (row: any, column: any, cellValue: string | undefined) => {
            return utc_to_local_format(cellValue);
        }
    } else if (key == "timems") {
        return (row: any, column: any, cellValue: number) => {
            return ms_to_s(cellValue);
        }
    } else if (key == "name") {
        return (row: any, column: any, cellValue: string) => {
            return cellValue;
        }
    } else {
        return (row: any, column: any, cellValue: string | number | undefined) => {
            return to_fixed_n(cellValue, index_tags[key].to_fixed);
        }
    }
}

onMounted(() => {
    document.getElementsByClassName("el-pagination__goto")[0].childNodes[0].nodeValue = "转到";
    // 把分页器的go to改成中文。
    mod_style();
    request_videos();
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

    index_visible.value = !["upload_time", "bbbv", "bbbv_s", "timems"].
        includes(index_tag_selected.value);
}

const prevColumn = ref<any>(null); //上一个排序列
const handleSortChange = (sort: any) => {
    console.log(sort);
    for (var key of Object.keys(index_tags)) { // 找到对应的key。很丑陋，but it works
        if (index_tags[key].key == sort.prop) {
            if (key != index_tag_selected.value) { // 改变了排序列，清除之前列的排序
                if (prevColumn.value != null) {
                    prevColumn.value.order = null;
                }
                index_tag_selected.value = key;
            }
            if (sort.order == null) { // 不允许通过点击箭头的方式将排序变成 null
                sort.column.order = state.ReverseOrder ? "descending" : "ascending";
            }
            state.ReverseOrder = sort.column.order == "descending"
            break;
        }
    }
    prevColumn.value = sort.column;
    request_videos();
}

const handleSizeChange = (val: number) => {
    state.PageSize = val;
    request_videos();
}

const handleCurrentChange = (val: number) => {
    state.CurrentPage = val;
    request_videos();
}

const offsetIndex = (index: number) => {
    return state.CurrentPage > 1 ? index + 1 + (state.CurrentPage - 1) * state.PageSize :
        [..."🥇🥈🥉🏅🏅🏅🏅🏅🏅🏅", 11, 12, 13, 14, 15, 16, 17, 18, 19, 20][index];
}

// 根据配置，刷新当前页面的录像表
const request_videos = () => {
    proxy.$axios.get('/video/query/',
        {
            params: {
                level: level_tags[level_tag_selected.value].key,
                mode: mode_tags[mode_tag_selected.value].key,
                o: index_tags[index_tag_selected.value].key, // order by
                r: state.ReverseOrder, // reverse order
                ps: state.PageSize, // page size
                page: state.CurrentPage,
            }
        }
    ).then(function (response) {
        const data = JSON.parse(response.data);
        videoList.splice(0, videoList.length);
        videoList.push(...data.videos);
        state.VideoCount = data.count;
    }).catch(() => {
        // 触发限流
        ElMessage.error({ message: '请稍后再试', offset: 68 });
    })
}

const index_select = (key: string | number, value: NameKeyReverse) => {
    index_tags[key].selected = !value.selected;
}

const preview = (row: any) => {
    var id = row.id
    if (!id) {
        return
    }
    (window as any).flop = null;
    preview_visible.value = true;
    proxy.$axios.get('/video/get_software/',
        {
            params: {
                id,
            }
        }
    ).then(function (response) {
        let uri = process.env.VUE_APP_BASE_API + "/video/preview/?id=" + id;
        // console.log(uri);
        if (response.data.msg == "a") {
            uri += ".avf";
        } else if (response.data.msg == "e") {
            uri += ".evf";
        }

        if ((window as any).flop) {
            playVideo(uri);
        } else {
            (window as any).flop = {
                onload: async function () {
                    playVideo(uri);
                },
            }
        }
    }).catch(
        (res) => {
            // console.log("报错");
            // console.log(res);
        }
    )
}


const playVideo = function (uri: string) {
    (window as any).flop.playVideo(uri, {
        share: {
            uri: uri,
            pathname: "/flop-player/player",
            anonymous: false,
            background: "rgba(100, 100, 100, 0.05)",
            title: "Flop Player Share",
            favicon: "https://avatars.githubusercontent.com/u/38378650?s=32", // 胡帝的头像
        },
        anonymous: false,
        background: "rgba(0, 0, 0, 0)",
        listener: function () {
            preview_visible.value = false;
            (window as any).flop = null;
        },
    });
}


</script>


<style lang="less" scoped>
.rank {
    width: 5%;
    display: inline-block;
    text-align: center;
}

.utime {
    width: 25%;
    min-width: 200px;
    display: inline-block;
    text-align: center;
}

:deep(.name) {
    width: 16%;
    display: inline-block;
    text-align: center;
}

.bbbv_bbbvs_rtime {
    width: 13%;
    min-width: 100px;
    display: inline-block;
    text-align: center;
}

.index {
    width: 13%;
    min-width: 100px;
    display: inline-block;
    text-align: center;
    // cursor: pointer;
}


.hoverable:hover {
    // color: rgb(64, 158, 255);
    cursor: pointer;
}

.el-pagination {
    justify-content: center;
}

.row {
    padding-top: 6px;
    padding-bottom: 6px;
}

.row:hover {
    background-color: #eee;
}

.inline-div {
    display: inline-block;
    margin: 0;
}
</style>
