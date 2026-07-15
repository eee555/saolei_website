<template>
    <ElButton @click="getLogDir">
        获取日志目录
    </ElButton>
    <ElTable :data="fileStats">
        <ElTableColumn prop="name" label="文件名" width="180" />
        <ElTableColumn prop="size" label="大小" width="180" />
        <ElTableColumn prop="mtime" label="修改时间" />
        <ElTableColumn label="操作" width="180">
            <template #default="scope">
                <ElButton @click="viewLog(scope.row.name)">
                    查看
                </ElButton>
                <ElButton @click="downloadLog(scope.row.name)">
                    下载
                </ElButton>
            </template>
        </ElTableColumn>
    </ElTable>
    <div class="log-toolbar">
        <span v-if="selectedLog">
            {{ selectedLog }}
        </span>
        <span>
            {{ streamStatus }}
        </span>
    </div>
    <pre class="log-viewer">{{ logContent }}</pre>
</template>

<script lang="ts" setup>
import { ElButton, ElTable, ElTableColumn } from 'element-plus';
import { onBeforeUnmount, onMounted, ref } from 'vue';

import { httpErrorNotification } from '@/components/Notifications';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

interface FileStat {
    name: string;
    size: number;
    mtime: string;
}

interface LogTailResponse {
    content: string;
    offset: number;
    size: number;
    truncated: boolean;
}

interface LogStreamMessage {
    content: string;
    offset: number;
}

defineOptions({ name: 'StaffLogs' });

const LOG_TAIL_BYTES = 64 * 1024;
const MAX_VISIBLE_LOG_CHARS = 1024 * 1024;

const { proxy } = useCurrentInstance();
const fileStats = ref([] as FileStat[]);
const logContent = ref('');
const selectedLog = ref('');
const streamStatus = ref('未连接');
let logEventSource: EventSource | null = null;

function closeLogStream() {
    if (logEventSource === null) {
        return;
    }
    logEventSource.close();
    logEventSource = null;
}

function makeApiUrl(path: string, params: Record<string, string | number>) {
    const rawBaseApi = import.meta.env.VITE_BASE_API as string | undefined;
    const baseApi = rawBaseApi ?? window.location.origin;
    const url = new URL(path, new URL(baseApi, window.location.origin));
    for (const [key, value] of Object.entries(params)) {
        url.searchParams.set(key, String(value));
    }
    return url.toString();
}

function appendLogContent(content: string) {
    logContent.value += content;
    if (logContent.value.length > MAX_VISIBLE_LOG_CHARS) {
        logContent.value = logContent.value.slice(-MAX_VISIBLE_LOG_CHARS);
    }
}

function openLogStream(log: string, offset: number) {
    closeLogStream();
    streamStatus.value = '正在连接实时更新';
    logEventSource = new EventSource(makeApiUrl('/api/common/staff/logstream', {
        filename: log,
        offset,
        tail_bytes: LOG_TAIL_BYTES,
    }), { withCredentials: true });
    logEventSource.onopen = () => {
        streamStatus.value = '实时更新中';
    };
    logEventSource.onmessage = (event) => {
        const data = JSON.parse(event.data) as LogStreamMessage;
        appendLogContent(data.content);
    };
    logEventSource.addEventListener('reset', () => {
        logContent.value = '[日志文件已被截断或轮转，正在从新文件继续读取]\n';
    });
    logEventSource.addEventListener('deleted', () => {
        streamStatus.value = '日志文件已删除';
        closeLogStream();
    });
    logEventSource.onerror = () => {
        streamStatus.value = '实时连接中断，浏览器将自动重连';
    };
}

function getLogDir() {
    proxy.$axios.get('/api/common/staff/logs').then(
        function (response) {
            fileStats.value = response.data;
        },
    ).catch(httpErrorNotification);
}

function viewLog(log: string) {
    closeLogStream();
    selectedLog.value = log;
    streamStatus.value = '正在加载日志尾部';
    proxy.$axios.get('/api/common/staff/logtail', { params: { filename: log, tail_bytes: LOG_TAIL_BYTES } }).then(
        function (response) {
            const data = response.data as LogTailResponse;
            logContent.value = data.truncated
                ? `[仅显示最后 ${LOG_TAIL_BYTES} 字节]\n${data.content}`
                : data.content;
            openLogStream(log, data.offset);
        },
    ).catch((error: unknown) => {
        streamStatus.value = '加载失败';
        httpErrorNotification(error);
    });
}

function downloadLog(log: string) {
    proxy.$axios.get('/api/common/staff/logview', { params: { filename: log }, responseType: 'blob' }).then(
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

onMounted(getLogDir);
onBeforeUnmount(closeLogStream);
</script>

<style scoped>
.log-toolbar {
    display: flex;
    gap: 1rem;
    margin: 1rem 0 0.5rem;
}

.log-viewer {
    max-height: 70vh;
    overflow: auto;
    padding: 1rem;
    border: 1px solid var(--el-border-color);
    border-radius: 4px;
    background: var(--el-fill-color-light);
    color: var(--el-text-color-primary);
    font-family: Consolas, Monaco, monospace;
    font-size: 0.875rem;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-all;
}
</style>
