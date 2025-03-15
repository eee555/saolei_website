<template>
    <el-table :data="videos_trans" :show-header="showHeader" table-layout="auto" :max-height="maxHeight" style="width: 100%;font-size: 16px;user-select: none;" @row-click="(row: any) => preview(row.key)">
        <el-table-column prop="state" :width="32"
            :filters="[{ text: t('common.state.c'), value: 'c' }, { text: t('common.state.d'), value: 'd' }]"
            :filter-method="defaultFilterMethod">
            <template #default="scope">
                <VideoStateIcon :state="scope.row.state" />
            </template>
        </el-table-column>
        <el-table-column :prop="upload_time" min-width="160" :formatter="simple_formatter(utc_to_local_format)"
            sortable />
        <el-table-column v-if="need_player_name" min-width="80">
            <template #default="player">
                <PlayerName class="name" :user-id="+player.row.player_id" :user-name="player.row.player"></PlayerName>
            </template>
        </el-table-column>
        <el-table-column min-width="20">
            <template #default="scope">
                <SoftwareIcon :software="scope.row.software" />
            </template>
        </el-table-column>
        <el-table-column
            :filters="[{ text: t('common.level.b'), value: 'b' }, { text: t('common.level.i'), value: 'i' }, { text: t('common.level.e'), value: 'e' }]"
            :filter-method="defaultFilterMethod" :filter-multiple="false">
            <template #default="scope">
                <GameLevelIcon :level="scope.row.level" />
            </template>
        </el-table-column>
        <el-table-column prop="mode" :formatter="simple_formatter((mode: string) => t('common.mode.' + mode))"
            :filters="[{ text: t('common.mode.std'), value: 'std' }, { text: t('common.mode.nf'), value: 'nf' }, { text: t('common.mode.ng'), value: 'ng' }, { text: t('common.mode.dg'), value: 'dg' }]"
            :filter-method="defaultFilterMethod" :filter-multiple="false" />
        <el-table-column prop="timems" :formatter="simple_formatter((timems: number) => (ms_to_s(timems) + 's'))"
            sortable />
        <el-table-column prop="bv" sortable />
        <!-- <el-table-column min-width="200">
            <template #default="scope">
                <PreviewDownload :id="scope.row.key"></PreviewDownload>
            </template>
        </el-table-column> -->
    </el-table>
</template>

<script setup lang="ts">
// 录像列表的组件

import { computed } from 'vue'
import { utc_to_local_format } from "@/utils/system/tools";
import PlayerName from '@/components/PlayerName.vue';
import VideoStateIcon from '@/components/widgets/VideoStateIcon.vue';
import SoftwareIcon from '@/components/widgets/SoftwareIcon.vue';
import GameLevelIcon from './widgets/GameLevelIcon.vue';
import { preview } from '@/utils/common/PlayerDialog';

import { ms_to_s, simple_formatter, defaultFilterMethod } from '@/utils';
import { useI18n } from 'vue-i18n';
import { ElTable, ElTableColumn } from 'element-plus';

const { t } = useI18n();

const data = defineProps({
    videos: {
        type: Array,
        default() { return [] },
    },
    // 反序
    reverse: {
        type: Boolean,
        default: false
    },
    // 需要用可以点开摘要的用户组件
    needPlayerName: {
        type: Boolean,
        default: true
    },
    reviewMode: {
        type: Boolean,
        default: false
    },
    uploadTime: {
        type: String,
        default: 'upload_time',
    },
    showHeader: {
        type: Boolean,
        default: true,
    },
    maxHeight: {
        type: [String, Number],
        default: '100%',
    },
})

defineEmits(['update'])

const videos_trans = computed(() => {
    const d = data.videos.slice();
    d.forEach((v: any) => {
        if (v.mode == "00") {
            v.mode = "std";
        } else if (v.mode == "01") {
            v.mode = "UPK";
        } else if (v.mode == "04") {
            v.mode = "Win7";
        } else if (v.mode == "05") {
            v.mode = "ng";
        } else if (v.mode == "06") {
            v.mode = "sng";
        } else if (v.mode == "07") {
            v.mode = "弱无猜";
        } else if (v.mode == "08") {
            v.mode = "准无猜";
        } else if (v.mode == "09") {
            v.mode = "强可猜";
        } else if (v.mode == "10") {
            v.mode = "弱可猜";
        } else if (v.mode == "11") {
            v.mode = "dg";
        } else if (v.mode == "12") {
            v.mode = "nf";
        }
    })

    if (data.reverse) {
        d.reverse();
    }
    return d;
})

</script>
<style lang="less" scoped>

.el-table .cell {
    line-height: 18px;
    padding: 0px 5px;
}

</style>