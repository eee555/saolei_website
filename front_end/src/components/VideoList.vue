<template>
    <Teleport to=".common-layout">
        <el-dialog v-model="preview_visible"
            style="backdrop-filter: blur(1px);" draggable align-center
            destroy-on-close :modal="false" :lock-scroll="false">
            <iframe class="flop-player-iframe flop-player-display-none" style="width: 100%; height: 500px; border: 0px"
                src="/flop/index.html" ref="video_iframe"></iframe>
        </el-dialog>
    </Teleport>
    <el-table :data="videos_trans" :show-header="false" @row-click="preview" table-layout="auto"
        style="width: 100%;font-size: 16px;user-select: none;">
        <el-table-column prop="time" min-width="200" :formatter="simple_formatter(utc_to_local_format)"/>
        <el-table-column v-if="need_player_name" min-width="80">
            <template #default="player">
                <PlayerName class="name" :user_id="+player.row.player_id" :user_name="player.row.player"></PlayerName>
            </template>
        </el-table-column>
        <el-table-column v-else prop="player" min-width="80" />
        <el-table-column prop="level" :formatter="simple_formatter((l: string) => $t('common.level.'+l))"/>
        <el-table-column prop="mode"/>
        <el-table-column prop="timems" :formatter="simple_formatter((timems: number) => (ms_to_s(timems) + 's'))"/>
        <el-table-column prop="bv" />
        <el-table-column style="white-space: nowrap;">
            <template #default="scope">
                <el-button v-if="review_mode" type="success" circle :icon="Check" @click.stop="handleApprove(scope.row)" />
                <el-button v-if="store.user.is_staff" type="danger" circle :icon="Close"
                    @click.stop="handleFreeze(scope.row)" />
            </template>
        </el-table-column>
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
import { Check, Close } from '@element-plus/icons-vue';
import { ElNotification } from 'element-plus';

import { useUserStore } from '@/store';
const store = useUserStore()

import { ms_to_s, approve, freeze, simple_formatter } from '@/utils';
import { generalNotification } from '@/utils/system/status';
import { useI18n } from 'vue-i18n';
const { proxy } = useCurrentInstance();

const t = useI18n();

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
    },
    review_mode: {
        type: Boolean,
        default: false
    },
})

const emit = defineEmits(['update'])

const videos_trans = computed(() => {
    const d = data.videos.slice();
    d.forEach((v: any) => {
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
        d.reverse();
    }
    return d;
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
        let uri = import.meta.env.VITE_BASE_API + "/video/preview/?id=" + row.key;
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
    }).catch((error: any) => {
        generalNotification(t, error.response.status, t.t('common.action.getSoftware'));
    })
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

const handleApprove = async function (row: any) {
    let status = await approve(proxy, row.key);
    if (status == 'True') {
        ElNotification({
            title: '审核成功',
            message: '录像已通过审核',
            type: 'success',
        })
    } else if (status == 'False') {
        ElNotification({
            title: '审核失败',
            message: '录像已通过审核',
            type: 'warning',
        })
    } else {
        ElNotification({
            title: '审核失败',
            message: '发生未知错误: status=' + status,
            type: 'error',
        })
    }
    emit('update')
}

const handleFreeze = async function (row: any) {
    let status = await freeze(proxy, row.key);
    if (status == 'True') {
        ElNotification({
            title: '冻结成功',
            message: '录像已冻结',
            type: 'success',
        })
    } else if (status == 'False') {
        ElNotification({
            title: '冻结失败',
            message: '录像已冻结',
            type: 'warning',
        })
    } else {
        ElNotification({
            title: '冻结失败',
            message: '发生未知错误: status=' + status,
            type: 'error',
        })
    }
    emit('update')
}

</script>
<style></style>