<template>
    <Teleport to=".common-layout">
        <el-dialog v-model="preview_visible"
            style="background-color: rgba(240, 240, 240, 0.48); backdrop-filter: blur(1px);" draggable align-center
            destroy-on-close :modal="false" :lock-scroll="false">
            <iframe class="flop-player-iframe flop-player-display-none" style="width: 100%; height: 500px; border: 0px"
                src="/flop/index.html" ref="video_iframe"></iframe>
        </el-dialog>
    </Teleport>
    <el-table :data="videos_trans" :show-header="false" @row-click="preview"
        style="width: 100%; color: black;font-size: 16px;">
        <el-table-column prop="time" min-width="200" />
        <el-table-column v-if="need_player_name" min-width="80">
            <template #default="player">
                <PlayerName class="name" :user_id="+player.row.player_id" :user_name="player.row.player"></PlayerName>
            </template>
        </el-table-column>
        <el-table-column v-else prop="player" min-width="80" />
        <el-table-column prop="level" min-width="80" />
        <el-table-column prop="mode" min-width="80" />
        <el-table-column prop="timems" min-width="90" />
        <el-table-column prop="bv" min-width="60" />
        <!-- <el-table-column min-width="200">
            <template #default="scope">
                <PreviewDownload :id="scope.row.key"></PreviewDownload>
            </template>
        </el-table-column> -->
    </el-table>
</template>

<script setup lang="ts">
// 录像列表的组件

import { ref, watch, computed } from 'vue'
import { utc_to_local_format } from "@/utils/system/tools";
import PlayerName from '@/components/PlayerName.vue';
const preview_visible = ref(false);
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import { getRowIdentity } from 'element-plus/es/components/table/src/util';
const { proxy } = useCurrentInstance();

const data = defineProps({
    videos: {
        type: Array,
        default: []
    },
    // 反序
    reverse: {
        type: Boolean,
        default: false
    },
    // 需要用可以点开摘要的用户组件
    need_player_name: {
        type: Boolean,
        default: true
    }
})

const videos_trans = computed(() => {
    data.videos.forEach((v: any) => {
        v.time = utc_to_local_format(v.time);
        if (v.level == "b") {
            v.level = "初级";
        } else if (v.level == "i") {
            v.level = "中级";
        } else if (v.level == "e") {
            v.level = "高级";
        }
        v.timems += "s";
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
            v.mode = "标准NF";
        }
    })
    if (data.reverse) {
        data.videos.reverse();
    }
    return data.videos;
})

// console.log(videos_trans);


const preview = (row: any, column: any, event: Event) => {
    if (!row.key) {
        return
    }
    (window as any).flop = null;
    preview_visible.value = true;
    proxy.$axios.get('/video/get_software/',
        {
            params: {
                id: row.key,
            }
        }
    ).then(function (response) {
        let uri = process.env.VUE_APP_BASE_API + "/video/preview/?id=" + row.key;
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
<style></style>