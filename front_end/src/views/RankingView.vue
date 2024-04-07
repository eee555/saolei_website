<template>
    <el-row class="mb-4" style="margin-bottom: 10px;">
        <el-button v-for="(tag, key) in mode_tags" type="success" :plain="!(mode_tag_selected == key)" :size="'small'"
            @click="mode_tag_selected = key as string; get_player_rank(1);">{{ tag.name }}</el-button>
    </el-row>

    <el-row class="mb-4" style="margin-bottom: 10px;">
        <el-button v-for="(tag, key) in index_tags" type="primary" :plain="!(index_tag_selected == key)" :size="'small'"
            @click="index_tag_selected = key as string; mod_style(); get_player_rank(1);">{{ tag.name
            }}</el-button>
    </el-row>

    <div style="width: 80%;font-size:20px;margin: auto;margin-top: 10px;">
        <div style="border-bottom: 1px solid #555555;padding-bottom: 10px;">
            <span class="rank">排名</span>
            <span class="name">姓名</span>
            <span class="number_wid" :style="{ color: (level_selected === 'b' ? 'rgb(64, 158, 255)' : '') }"
                @click="setSortDirect('b')">初级{{
            level_selected === "b" ? (index_tags[index_tag_selected].reverse ? "▼" : "▲") : "" }}</span>
            <span class="number_wid" :style="{ color: (level_selected === 'i' ? 'rgb(64, 158, 255)' : '') }"
                @click="setSortDirect('i')">中级{{
            level_selected === "i" ? (index_tags[index_tag_selected].reverse ? "▼" : "▲") : "" }}</span>
            <span class="number_wid" :style="{ color: (level_selected === 'e' ? 'rgb(64, 158, 255)' : '') }"
                @click="setSortDirect('e')">高级{{
            level_selected === "e" ? (index_tags[index_tag_selected].reverse ? "▼" : "▲") : "" }}</span>
            <span class="sum_title" :style="{ color: (level_selected === 'sum' ? 'rgb(64, 158, 255)' : '') }"
                @click="setSortDirect('sum')">总计{{
            level_selected === "sum" ? (index_tags[index_tag_selected].reverse ? "▼" : "▲") : "" }}</span>
        </div>
        <div v-for="(player, key) in playerData" style="margin-top: 10px;">

            <span class="rank">{{ key - 19 + (state.CurrentPage) * 20 }}</span>
            <!-- <span class="name">{{ player.name }}</span> -->
            <PlayerName class="name" :user_id="player.name_id" :user_name="player.name"></PlayerName>
            <!-- <span class="beginner">{{ to_fixed_n(player.beginner, 3) }}</span> -->
            <span class="number_wid">
                <PreviewNumber :id="player.beginner_id" :text="to_fixed_n(player.beginner, 3)">
                </PreviewNumber>
            </span>
            <span class="number_wid">
                <PreviewNumber :id="player.intermediate_id" :text="to_fixed_n(player.intermediate, 3)">
                </PreviewNumber>
            </span>
            <span class="number_wid">
                <PreviewNumber :id="player.expert_id" :text="to_fixed_n(player.expert, 3)">
                </PreviewNumber>
            </span>
            
            <span class="sum">{{ to_fixed_n(player.sum, 3) }}</span>


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
import { onMounted, ref, Ref, reactive } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import { to_fixed_n } from "@/utils";
import PreviewNumber from '@/components/PreviewNumber.vue';
import PlayerName from '@/components/PlayerName.vue';
import { defineAsyncComponent } from 'vue'
// const AsyncPlayerName = defineAsyncComponent(() => import('@/components/PlayerName.vue'))
const { proxy } = useCurrentInstance();

// const level_tag_selected = ref("EXPERT");
const mode_tag_selected = ref("STD");
const index_tag_selected = ref("timems");
const level_selected = ref("sum"); // bie&sum

const index_visible = ref(true);

const state = reactive({
    tableLoading: false,
    CurrentPage: 1,
    // PageSize: 20,
    Total: 3,
});

// const test  = reactive({v: 5});
const playerData = reactive<Player[]>([]);
interface Player {
    name_id: number;
    name: string;
    beginner: string;
    beginner_id: number;
    intermediate: string;
    intermediate_id: number;
    expert: string;
    expert_id: number;
    sum: string;
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

const mode_tags: Tags = {
    "STD": { name: "标准", key: "std" },
    "NF": { name: "盲扫", key: "nf" },
    "JSW": { name: "竞速无猜", key: "ng" },
    "BZD": { name: "递归", key: "dg" }
}


// reverse: true从小到大
const index_tags: TagsReverse = {
    "timems": { name: "成绩", key: "timems", reverse: false, to_fixed: 3 },
    "bbbv_s": { name: "3BV/s", key: "bvs", reverse: true, to_fixed: 3 },
    "path": { name: "path", key: "path", reverse: false, to_fixed: 2 },
    "stnb": { name: "STNB", key: "stnb", reverse: true, to_fixed: 2 },
    "ioe": { name: "IOE", key: "ioe", reverse: true, to_fixed: 3 },
}

onMounted(() => {
    document.getElementsByClassName("el-pagination__goto")[0].childNodes[0].nodeValue = "转到";
    // 把分页器的go to改成中文。


    mod_style();
    get_player_rank(1);
})




const mod_style = () => {
    // 调整列宽样式
    // console.log(index_visible.value);

    index_visible.value = !["upload_time", "bbbv", "bbbv_s", "timems"].
        includes(index_tag_selected.value);
}

const get_player_rank = (page: number) => {
    state.CurrentPage = page
    const iv = index_tags[index_tag_selected.value];
    const mv = mode_tags[mode_tag_selected.value];
    const piv = `player_${iv.key}_${mv.key}_`;
    proxy.$axios.get('/msuser/player_rank/',
        {
            params: {
                ids: `${piv}ids`,
                sort_by: `${piv}*->${level_selected.value}`,
                reverse: iv.reverse,
                indexes: `["#","${piv}*->name","${piv}*->b","${piv}*->b_id","${piv}*->i","${piv}*->i_id","${piv}*->e","${piv}*->e_id","${piv}*->sum"]`,
                page: page,
            }
        }
    ).then(function (response) {
        // console.log(response.data);
        const data = response.data;
        state.Total = data.total_page;

        const players = data.players;
        playerData.splice(0, playerData.length)
        for (let i = 0; i < players.length / 9; i++) {
            playerData.push({
                name_id: +players[i * 9],
                name: players[i * 9 + 1],
                beginner: players[i * 9 + 2],
                beginner_id: +players[i * 9 + 3],
                intermediate: players[i * 9 + 4],
                intermediate_id: +players[i * 9 + 5],
                expert: players[i * 9 + 6],
                expert_id: +players[i * 9 + 7],
                sum: players[i * 9 + 8],
            })
        }
        // console.log(playerData);

    })
}

const currentChange = (val: number) => {
    state.CurrentPage = Math.ceil(val);
    get_player_rank(state.CurrentPage);
}
// 上一页
const prevClick = () => {
    state.CurrentPage = state.CurrentPage - 1;
    if (state.CurrentPage < 1) {
        state.CurrentPage = 1;
    }
    get_player_rank(state.CurrentPage);
}
// 下一页
const nextClick = () => {
    state.CurrentPage = state.CurrentPage + 1;
    if (state.CurrentPage > state.Total) {
        state.CurrentPage = state.Total;
    }
    get_player_rank(state.CurrentPage);
}

// 点难度标签右侧排序方向箭头的回调
const setSortDirect = (level_tag: string) => {
    if (level_tag === level_selected.value) {
        index_tags[index_tag_selected.value].reverse = !index_tags[index_tag_selected.value].reverse;
    } else {
        level_selected.value = level_tag;
    }
    get_player_rank(state.CurrentPage);
}

</script>


<style lang="less" scoped>
.rank {
    width: 10%;
    display: inline-block;
}

:deep(.name) {
    width: 24%;
    min-width: 150px;
    display: inline-block;
    text-align: center;
}

.number_wid {
    width: 16%;
    min-width: 100px;
    display: inline-block;
    text-align: center;
}

.number_wid:hover {
    color: rgb(64, 158, 255);
    cursor: pointer;
}

.sum {
    width: 16%;
    min-width: 100px;
    display: inline-block;
    text-align: center;
}

.sum_title {
    width: 16%;
    min-width: 100px;
    display: inline-block;
    text-align: center;
}

.sum_title:hover {
    color: rgb(64, 158, 255);
    cursor: pointer;
}

.el-pagination {
    justify-content: center;
}
</style>
