<template>
    <el-table :data="videos" table-layout="auto" size="small" :height="height" style="min-width: 100%;font-size: 16px;user-select: none;" :cell-style="{padding: 0}" :default-sort="{prop: 'upload_time', order: 'descending'}" @row-click="(row: any) => preview(row.id)">
        <ColumnState />
        <ColumnUploadTime :sortable="sortable" />
        <ColumnPlayerName v-if="needPlayerName" />
        <ColumnSoftware />
        <ColumnLevel />
        <ColumnMode />
        <ColumnStat :sortable="sortable" stat="time" />
        <ColumnStat :sortable="sortable" stat="bv" />
        <ColumnStat :sortable="sortable" stat="bvs" />
        <ColumnStat :sortable="sortable" stat="ioe" />
        <ColumnStat :sortable="sortable" stat="thrp" />
        <ColumnFileSize v-if="fileSize" :sortable="sortable" />
    </el-table>
</template>

<script setup lang="ts">
// 录像列表的组件
import { preview } from '@/utils/common/PlayerDialog';
import { ElTable } from 'element-plus';
import { VideoAbstract } from '@/utils/videoabstract';
import ColumnFileSize from './VideoList/ColumnFileSize.vue';
import ColumnMode from './VideoList/ColumnMode.vue';
import ColumnLevel from './VideoList/ColumnLevel.vue';
import ColumnState from './VideoList/ColumnState.vue';
import ColumnPlayerName from './VideoList/ColumnPlayerName.vue';
import ColumnStat from './VideoList/ColumnStat.vue';
import ColumnSoftware from './VideoList/ColumnSoftware.vue';
import ColumnUploadTime from './VideoList/ColumnUploadTime.vue';

defineProps({
    videos: {
        type: Array<VideoAbstract>,
        default() { return []; },
    },
    // 反序
    reverse: {
        type: Boolean,
        default: false,
    },
    // 需要用可以点开摘要的用户组件
    needPlayerName: {
        type: Boolean,
        default: true,
    },
    reviewMode: {
        type: Boolean,
        default: false,
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
    fileSize: {
        type: Boolean,
        default: false,
    },
});

</script>
