<template>
    <el-button @click="getLogDir">获取日志目录</el-button>
    <el-table :data="fileStats">
        <el-table-column prop="name" label="文件名" width="180"></el-table-column>
        <el-table-column prop="size" label="大小" width="180"></el-table-column>
        <el-table-column prop="mtime" label="修改时间"></el-table-column>
        <el-table-column label="操作" width="180">
            <template #default="scope">
                <el-button @click="viewLog(scope.row.name)">查看</el-button>
                <el-button @click="downloadLog(scope.row.name)">下载</el-button>
            </template>
        </el-table-column>
    </el-table>
    <code-highlight language="log">
        {{ logContent }}
    </code-highlight>
</template>

<script lang="ts" setup>

import { ElButton, ElTable, ElTableColumn } from 'element-plus';
import { ref } from 'vue';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { httpErrorNotification } from '../Notifications';
import CodeHighlight from 'vue-code-highlight/src/CodeHighlight.vue';

interface FileStat {
    name: string;
    size: number;
    mtime: Date;
}

const { proxy } = useCurrentInstance();
const fileStats = ref([] as FileStat[]);
const logContent = ref('');

function getLogDir() {
    proxy.$axios.get('logs/').then(
        function (response) {
            fileStats.value = response.data;
        },
    ).catch(httpErrorNotification);
}

function viewLog(log: string) {
    proxy.$axios.get('log_view/', { params: { filename: log } }).then(
        function (response) {
            logContent.value = response.data;
        },
    ).catch(httpErrorNotification);
}

function downloadLog(log: string) {
    proxy.$axios.get('log_view/', { params: { filename: log } }).then(
        function (response) {
            const blob = new Blob([response.data], { type: 'application/octet-stream' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = log;
            a.click();
            window.URL.revokeObjectURL(url);
        },
    ).catch(httpErrorNotification);
}

</script>
