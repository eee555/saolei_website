<template>
    <el-row class="mb-4" style="margin-bottom: 10px;">
        <el-button v-for="(tag, key) in level_tags" type="warning" :plain="!(level_tag_selected == key)" :size="'small'"
            @click="level_tag_selected = key as string; request_videos();">{{ t('common.level.' + tag.key)
            }}</el-button>
    </el-row>

    <el-row class="mb-4" style="margin-bottom: 10px;">
        <el-button v-for="(tag, key) in mode_tags" type="success" :plain="!(mode_tag_selected == key)" size="small"
            @click="mode_tag_selected = key as string; request_videos();">{{ tag.name }}</el-button>
    </el-row>

    <el-row class="mb-4" style="margin-bottom: 10px;">
        <el-button v-for="(value, key) in index_tags" type="primary" :plain="!value.selected" size="small"
            @click="index_select(key, value)">{{ t('common.prop.' + key)
            }}</el-button>
    </el-row>

    <el-descriptions :title="t('common.filter')">
        <el-descriptions-item :label="t('common.prop.state')">
            <VideoStateFilter v-model="videofilter.filter_state" @change="request_videos" />
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.prop.bbbv')">
            <BBBVFilter @change="request_videos" :level="level_tags[level_tag_selected].key"/>
        </el-descriptions-item>
    </el-descriptions>
    <div style="font-size:20px;margin: auto;margin-top: 10px;">
        <el-table :data="videoList" @sort-change="handleSortChange" @row-click="(row: any) => preview(row.id)" border
            table-layout="auto">
            <VideoViewState />
            <el-table-column type="index" :index="offsetIndex" fixed></el-table-column>
            <VideoViewRealname />
            <el-table-column v-for="key in selected_index()" :prop="index_tags[key].key"
                :label="t('common.prop.' + key)" sortable="custom"
                :sort-orders="index_tags[key].reverse ? (['descending', 'ascending']) : (['ascending', 'descending'])"
                v-slot="scope">
                <span class="nobr">{{ columnFormatter(key, scope.row[index_tags[key].key]) }}</span>
            </el-table-column>
        </el-table>
    </div>

    <div style="margin-top: 16px;">
        <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange"
            :current-page="state.CurrentPage" :page-sizes="[20, 50, 100]" :page-size="videofilter.pagesize"
            layout="total, sizes, prev, pager, next, jumper" :total="state.VideoCount">
        </el-pagination>
    </div>
</template>

<script lang="ts" setup>
// 全网录像的检索器，根据三个维度排序
import { onMounted, ref, reactive } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";

import VideoStateFilter from '@/components/Filters/VideoStateFilter.vue';
import BBBVFilter from '@/components/Filters/BBBVFilter.vue';

import VideoViewRealname from '@/components/tableColumns/VideoViewRealname.vue';
import VideoViewState from '@/components/tableColumns/VideoViewState.vue';

const { proxy } = useCurrentInstance();
import { utc_to_local_format } from "@/utils/system/tools";
import { ms_to_s } from "@/utils";
import { preview } from '@/utils/common/PlayerDialog';

import { useI18n } from 'vue-i18n';
const { t } = useI18n();

import { videofilter } from '@/store';
import { httpErrorNotification } from '@/components/Notifications';

const level_tag_selected = ref("EXPERT");
const mode_tag_selected = ref("STD");
const index_tag_selected = ref("timems");

const index_visible = ref(true);

const state = reactive({
    tableLoading: false,
    CurrentPage: 1,
    VideoCount: 0,
    ReverseOrder: false,
    Total: 3
});

// const test  = reactive({v: 5});
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
    key: string;
    reverse: boolean;
    to_fixed: number;
    selected: boolean;
}
interface TagsReverse {
    [index: string]: NameKeyReverse;
}

interface LevelTag {
    [index: string]: {
        key: string,
        min: number,
        max: number,
    }
}

const level_tags: LevelTag = reactive({
    "BEGINNER": { key: "b", min: 1, max: 54 },
    "INTERMEDIATE": { key: "i", min: 30, max: 216 },
    "EXPERT": { key: "e", min: 100, max: 381 },
});

const mode_tags: Tags = {
    "STD": { name: "标准", key: "00" },
    "NF": { name: "盲扫", key: "12" },
    //"UPK": { name: "UPK", key: "01" },
    "WQI": { name: "Win7", key: "04" },
    "JSW": { name: "竞速无猜", key: "05" },
    "QWC": { name: "强无猜", key: "06" },
    "RWC": { name: "弱无猜", key: "07" },
    //"ZWC": { name: "准无猜", key: "08" },
    //"QKC": { name: "强可猜", key: "09" },
    //"RKC": { name: "弱可猜", key: "10" },
    //"BZD": { name: "递归", key: "11" }
}


// reverse: true从小到大
const index_tags: TagsReverse = reactive({
    "upload_time": { key: "upload_time", reverse: true, to_fixed: -1, selected: true },
    // "name": { name: "姓名", key: "player__realname", reverse: false, to_fixed: 0, selected: true},
    "timems": { key: "timems", reverse: false, to_fixed: 3, selected: true },
    "bbbv": { key: "bv", reverse: false, to_fixed: 0, selected: true },
    "bbbv_s": { key: "bvs", reverse: true, to_fixed: 3, selected: true },
    "left_s": { key: "video__left_s", reverse: true, to_fixed: 3, selected: false },
    "right_s": { key: "video__right_s", reverse: true, to_fixed: 3, selected: false },
    "double_s": { key: "video__double_s", reverse: true, to_fixed: 3, selected: false },
    "cl_s": { key: "video__cl_s", reverse: true, to_fixed: 3, selected: false },
    "path": { key: "video__path", reverse: false, to_fixed: 2, selected: false },
    "stnb": { key: "video__stnb", reverse: true, to_fixed: 2, selected: true },
    "ioe": { key: "video__ioe", reverse: true, to_fixed: 3, selected: false },
    "thrp": { key: "video__thrp", reverse: true, to_fixed: 3, selected: false },
    "ce_s": { key: "video__ce_s", reverse: true, to_fixed: 3, selected: false },
    "op": { key: "video__op", reverse: false, to_fixed: 0, selected: false },
    "is": { key: "video__isl", reverse: false, to_fixed: 0, selected: false },
    "cell1": { key: "video__cell1", reverse: false, to_fixed: 0, selected: false },
    "cell2": { key: "video__cell2", reverse: false, to_fixed: 0, selected: false },
    "cell3": { key: "video__cell3", reverse: false, to_fixed: 0, selected: false },
    "cell4": { key: "video__cell4", reverse: false, to_fixed: 0, selected: false },
    "cell5": { key: "video__cell5", reverse: false, to_fixed: 0, selected: false },
    "cell6": { key: "video__cell6", reverse: false, to_fixed: 0, selected: false },
    "cell7": { key: "video__cell7", reverse: false, to_fixed: 0, selected: false },
    "cell8": { key: "video__cell8", reverse: false, to_fixed: 0, selected: false }
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

const columnFormatter = (key: string, value: any) => {
    if (key == "upload_time") {
        return utc_to_local_format(value);
    } else if (key == "timems") {
        return ms_to_s(value);
    } else if (key == "name") {
        return value;
    } else {
        return to_fixed_n(value, index_tags[key].to_fixed);
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
    videofilter.pagesize = val;
    request_videos();
}

const handleCurrentChange = (val: number) => {
    state.CurrentPage = val;
    request_videos();
}

const offsetIndex = (index: number) => {
    return index + 1 + (state.CurrentPage - 1) * videofilter.pagesize;
}

// 根据配置，刷新当前页面的录像表
const request_videos = () => {
    let params: { [key: string]: any } = {};
    params["level"] = level_tags[level_tag_selected.value].key;
    params["mode"] = mode_tags[mode_tag_selected.value].key;
    params["o"] = index_tags[index_tag_selected.value].key;
    params["r"] = state.ReverseOrder;
    params["ps"] = videofilter.pagesize;
    params["page"] = state.CurrentPage;
    // @ts-expect-error
    params["bmin"] = videofilter.bbbv_range[level_tags[level_tag_selected.value].key][0];
    // @ts-expect-error
    params["bmax"] = videofilter.bbbv_range[level_tags[level_tag_selected.value].key][1];
    if (![0,4].includes(videofilter.filter_state.length)) {
        params['s'] = videofilter.filter_state;
    }
    proxy.$axios.get('/video/query/',
        {
            params: params,
        }
    ).then(function (response) {
        const data = JSON.parse(response.data);
        videoList.splice(0, videoList.length);
        videoList.push(...data.videos);
        state.VideoCount = data.count;
    }).catch(httpErrorNotification)
}

const index_select = (key: string | number, value: NameKeyReverse) => {
    index_tags[key].selected = !value.selected;
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

.nobr {
    white-space: nowrap;
    hyphens: none;
}
</style>
