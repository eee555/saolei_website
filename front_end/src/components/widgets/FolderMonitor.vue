<template>
    <div class="folder-monitor">
        <!-- 不支持时显示提示 -->
        <div v-if="!isSupported" class="text text-warning">
            浏览器不支持 File System Access API，无法监视文件夹变化。
        </div>

        <!-- 支持时显示操作面板 -->
        <div v-else>
            <ElButton v-if="!folderHandle" :disabled="isSelecting" @click="selectFolder">
                选择文件夹
            </ElButton>
            <ElButton v-else @click="stopPolling">
                停止轮询
            </ElButton>
            <span v-if="isSelecting" class="text text-warning"> 正在授权...</span>
            <span v-if="isPolling" class="text text-primary">
                当前文件夹: {{ folderName }}
            </span>
            <span class="text">
                轮询间隔：
            </span>
            <ElInputNumber v-model="local.folderMonitorPollingInterval" :min="1" :step="1000" controls-position="right" style="width: 6em" />
        </div>
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ElButton, ElInputNumber } from 'element-plus';
import { computed, onUnmounted, ref } from 'vue';

import { local } from '@/store';

// ---------- 类型声明（兼容旧版 TS）----------
// 如果已经安装 @types/wicg-file-system-access 则可删除此块
declare global {
    interface Window {
        // eslint-disable-next-line @typescript-eslint/method-signature-style
        showDirectoryPicker?(options?: {
            id?: string;
            mode?: 'read' | 'readwrite';
            startIn?: FileSystemHandle | 'desktop' | 'documents' | 'downloads' | 'music' | 'pictures' | 'videos';
        }): Promise<FileSystemDirectoryHandle>;
    }
}

// ---------- Emits ----------
const emit = defineEmits<{
    /** 当检测到新增文件时触发，传递 File 对象数组 */
    (e: 'new-files', files: File[]): void;
}>();

// ---------- 响应式状态 ----------
const isSupported = computed(() => !!(window.isSecureContext && window.showDirectoryPicker)); // 浏览器是否支持 API
const folderHandle = ref<FileSystemDirectoryHandle | null>(null);
const folderName = ref('');
const isSelecting = ref(false);
let pollTimer: ReturnType<typeof setInterval> | null = null;
const isPolling = ref(false);

// 文件快照：存储上一次轮询时存在的文件名集合
const previousFileNames = ref<Set<string>>(new Set());

/** 获取目录下所有直接子文件的 File 对象及其名称 */
async function getCurrentFiles(handle: FileSystemDirectoryHandle): Promise<Map<string, File>> {
    const fileMap = new Map<string, File>();
    // 注意：values() 会包含子目录，需要过滤
    for await (const entry of handle.values()) {
        if (entry.kind === 'file') {
            const fileHandle = entry;
            try {
                const file = await fileHandle.getFile();
                fileMap.set(file.name, file);
            } catch (err) {
                console.warn(`无法读取文件 ${entry.name}:`, err);
            }
        }
    }
    return fileMap;
}

/** 轮询任务：对比快照，找出新增文件并 emit */
async function poll() {
    if (!folderHandle.value) return;

    try {
        const currentFileMap = await getCurrentFiles(folderHandle.value);
        const currentFileNames = new Set(currentFileMap.keys());
        const previousNames = previousFileNames.value;

        // 找出新增的文件名
        const addedNames: string[] = [];
        for (const name of currentFileNames) {
            if (!previousNames.has(name)) {
                addedNames.push(name);
            }
        }

        if (addedNames.length > 0) {
            // 获取新增文件对应的 File 对象
            // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
            const addedFiles = addedNames.map((name) => currentFileMap.get(name)!).filter(Boolean);
            if (addedFiles.length) {
                emit('new-files', addedFiles);
            }
        }

        // 更新快照
        previousFileNames.value = currentFileNames;
    } catch (err) {
        console.error('轮询文件夹时出错:', err);
        // 可能权限丢失或句柄失效，停止轮询并提示用户重新选择
        stopPolling();
        folderHandle.value = null;
        folderName.value = '';
    }
}

/** 启动轮询 */
function startPolling() {
    if (pollTimer) clearInterval(pollTimer);
    if (!folderHandle.value) return;

    // 先立即执行一次，建立初始快照（不触发 emit）
    getCurrentFiles(folderHandle.value).
        then((map) => {
            previousFileNames.value = new Set(map.keys());
            isPolling.value = true;
            // 启动定时轮询
            pollTimer = setInterval(() => {
                void poll();
            }, local.value.folderMonitorPollingInterval);
        }).
        catch((err: unknown) => {
            console.error('初始化文件夹快照失败:', err);
            folderHandle.value = null;
            folderName.value = '';
        });
}

/** 停止轮询 */
function stopPolling() {
    if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
    }
    isPolling.value = false;
}

/** 用户选择文件夹 */
async function selectFolder() {
    if (!isSupported.value) return;
    isSelecting.value = true;
    try {
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        const handle = await window.showDirectoryPicker!({
            mode: 'read', // 只需要读取权限
        });
        previousFileNames.value.clear();
        folderHandle.value = handle;
        folderName.value = handle.name;
        // 启动新轮询
        startPolling();
    } catch (err: any) {
        if (err.name !== 'AbortError') {
            console.error('选择文件夹失败:', err);
            alert('无法访问该文件夹，请重试或检查权限。');
        }
    // 用户取消选择不做任何事
    } finally {
        isSelecting.value = false;
    }
}

// 当组件卸载时清理定时器
onUnmounted(() => {
    stopPolling();
});
</script>

<style scoped>
.folder-monitor {
    font-family: system-ui, sans-serif;
    padding: 0.5rem;
}
</style>
