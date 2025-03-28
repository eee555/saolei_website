<template>
    <el-table :data="videos" table-layout="auto" size="small" :height="height" style="min-width: 100%;font-size: 16px;user-select: none;" :cell-style="{padding: 0}" :default-sort="{prop: 'upload_time', order: 'descending'}" @row-click="(row: any) => preview(row.id)">
        <el-table-column 
            prop="state" :width="32"
            :filters="[{ text: t('common.state.c'), value: 'c' }, { text: t('common.state.d'), value: 'd' }]"
            :filter-method="defaultFilterMethod"
        >
            <template #default="scope">
                <VideoStateIcon :state="scope.row.state" />
            </template>
        </el-table-column>
        <el-table-column 
            prop="upload_time" min-width="180" :formatter="simple_formatter(utc_to_local_format)"
            :sortable="sortable"
        />
        <el-table-column v-if="needPlayerName" min-width="80">
            <template #default="player">
                <PlayerName class="name" :user-id="+player.row.player_id" :user-name="player.row.player_name" />
            </template>
        </el-table-column>
        <el-table-column width="32">
            <template #default="scope">
                <SoftwareIcon :software="scope.row.software" style="margin: 0 -8px;" />
            </template>
        </el-table-column>
        <el-table-column
            :filters="[{ text: t('common.level.b'), value: 'b' }, { text: t('common.level.i'), value: 'i' }, { text: t('common.level.e'), value: 'e' }]"
            :filter-method="defaultFilterMethod" :filter-multiple="false"
        >
            <template #default="scope">
                <GameLevelIcon :level="scope.row.level" />
            </template>
        </el-table-column>
        <el-table-column 
            prop="mode" :formatter="simple_formatter((mode: string) => t(`common.mode.code${mode}`))"
            :filters="[{ text: t('common.mode.code00'), value: '00' }, { text: t('common.mode.code12'), value: '12' }, { text: t('common.mode.code05'), value: '05' }, { text: t('common.mode.code11'), value: '11' }]"
            :filter-method="defaultFilterMethod" :filter-multiple="false"
        />
        <el-table-column prop="timems" :sortable="sortable" :label="t('common.prop.time')" align="right">
            <template #default="scope">
                {{ scope.row.displayStat('time') }}
            </template>
        </el-table-column>
        <el-table-column prop="bv" :sortable="sortable" :label="t('common.prop.bv')" align="right" />
        <el-table-column :label="t('common.prop.bvs')" align="right" :sortable="sortable" :sort-by="(row) => row.bvs()">
            <template #default="scope">
                {{ scope.row.displayStat('bvs') }}
            </template>
        </el-table-column>
        <el-table-column :label="t('common.prop.ioe')" align="right" :sortable="sortable" :sort-by="(row) => row.ioe()">
            <template #default="scope">
                {{ scope.row.displayStat('ioe') }}
            </template>
        </el-table-column>
        <el-table-column :label="t('common.prop.thrp')" align="right" :sortable="sortable" :sort-by="(row) => row.thrp()">
            <template #default="scope">
                {{ scope.row.displayStat('thrp') }}
            </template>
        </el-table-column>
    </el-table>
</template>

<script setup lang="ts">
// 录像列表的组件
import { utc_to_local_format } from "@/utils/system/tools";
import PlayerName from '@/components/PlayerName.vue';
import VideoStateIcon from '@/components/widgets/VideoStateIcon.vue';
import SoftwareIcon from '@/components/widgets/SoftwareIcon.vue';
import GameLevelIcon from './widgets/GameLevelIcon.vue';
import { preview } from '@/utils/common/PlayerDialog';

import { simple_formatter, defaultFilterMethod } from '@/utils';
import { useI18n } from 'vue-i18n';
import { ElTable, ElTableColumn } from 'element-plus';
import { VideoAbstract } from '@/utils/videoabstract';

const { t } = useI18n();

defineProps({
    videos: {
        type: Array<VideoAbstract>,
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
    showHeader: {
        type: Boolean,
        default: true,
    },
    sortable: {
        type: Boolean,
        default: false,
    },
    height: {
        type: [String, Number],
        default: '100%',
    },
})

</script>
