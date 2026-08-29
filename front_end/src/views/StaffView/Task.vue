<template>
    <ElDescriptions v-loading="summaryLoading" title="概览" border :column="5">
        <ElDescriptionsItem label="total">
            {{ taskSummary.total }}
        </ElDescriptionsItem>
        <ElDescriptionsItem
            v-for="status in DjangoTaskResultStatusOptions"
            :key="status"
            :label="status"
        >
            {{ taskSummary.status[status] ?? 0 }}
        </ElDescriptionsItem>
    </ElDescriptions>
    <PrToolbar>
        对于失败的任务，点击“FAILED”按钮可以在控制台输出报错。
        <template #start>
            <ElButton :loading="loading" @click="refresh">
                加载任务
            </ElButton>
            <ElButton :loading="cleanupLoading" @click="cleanupExpiredTasks">
                删除过期任务
            </ElButton>
            <ElButton :disabled="selectedTasks.length === 0" @click="deleteSelected">
                删除选中任务
            </ElButton>
        </template>
    </PrToolbar>
    <PrDataTable
        v-model:filters="filters"
        v-model:selection="selectedTasks"
        v-loading="loading"
        :value="taskData"
        filter-display="menu"
        paginator
        :rows="10"
        paginator-template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown JumpToPageInput CurrentPageReport"
    >
        <PrColumn selection-mode="multiple" />
        <PrColumn field="id" header="id" />
        <PrColumn field="status" header="status">
            <template #body="{ data }">
                <ElButton v-if="data.status === 'FAILED'" @click="console.log(data.traceback)">
                    {{ data.status }}
                </ElButton>
                <template v-else>
                    {{ data.status }}
                </template>
            </template>
            <template #filter="{ filterModel, filterCallback }">
                <PrSelect v-model="filterModel.value" :options="[...DjangoTaskResultStatusOptions]" @change="filterCallback()" />
            </template>
        </PrColumn>
        <PrColumn field="enqueued_at" header="enqueued_at" sortable>
            <template #body="{ data }">
                {{ toISODateTimeString(toDate(data.enqueued_at)!) }}
            </template>
        </PrColumn>
        <PrColumn field="started_at" header="started_at" sortable>
            <template #body="{ data }">
                {{ data.started_at ? toISODateTimeString(toDate(data.started_at)!) : 'N/A' }}
            </template>
        </PrColumn>
        <PrColumn field="finished_at" header="finished_at" sortable>
            <template #body="{ data }">
                {{ data.finished_at ? toISODateTimeString(toDate(data.finished_at)!) : 'N/A' }}
            </template>
        </PrColumn>
        <PrColumn field="args_kwargs" header="args_kwargs" />
        <PrColumn field="priority" header="priority" sortable />
        <PrColumn field="task_path" header="task_path" />
        <PrColumn field="worker_ids" header="worker_ids" />
        <PrColumn field="queue_name" header="queue_name" />
        <PrColumn field="backend_name" header="backend_name" />
        <PrColumn field="run_after" header="run_after" sortable>
            <template #body="{ data }">
                {{ toISODateTimeString(toDate(data.run_after)!) }}
            </template>
        </PrColumn>
        <PrColumn field="return_value" header="return_value" />
        <PrColumn field="exception_class_path" header="exception_class_path" />
        <PrColumn header="actions">
            <template #body="{ data }">
                <ElButton
                    v-if="data.status === 'FAILED'"
                    :loading="restartingTaskId === data.id"
                    @click="restartTask(data)"
                >
                    重启
                </ElButton>
            </template>
        </PrColumn>
    </PrDataTable>
</template>

<script setup lang="ts">
import { FilterMatchMode } from '@primevue/core/api';
import { ElButton, ElDescriptions, ElDescriptionsItem, vLoading } from 'element-plus';
import PrColumn from 'primevue/column';
import PrDataTable from 'primevue/datatable';
import PrSelect from 'primevue/select';
import PrToolbar from 'primevue/toolbar';
import { onMounted, ref } from 'vue';

import { httpErrorNotification } from '@/components/Notifications';
import { createEnumMap } from '@/utils';
import type { EnumMap } from '@/utils';
import type { DjangoTaskResultStatus } from '@/utils/common/structInterface';
import { DjangoTaskResultStatusOptions } from '@/utils/common/structInterface';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { toDate, toISODateTimeString } from '@/utils/datetime';

interface TaskDetail {
    id: string;
    status: DjangoTaskResultStatus;
    enqueued_at: string;
    started_at: string | null;
    finished_at: string | null;
    args_kwargs: {
        args: unknown[];
        kwargs: Record<string, unknown>;
    };
    priority: number;
    task_path: string;
    worker_ids: string[];
    queue_name: string;
    backend_name: string;
    run_after: string;
    return_value: unknown;
    exception_class_path: string;
    traceback: string;
}

interface TaskSummary {
    total: number;
    status: EnumMap<DjangoTaskResultStatus, number>;
}

const { proxy } = useCurrentInstance();

const taskData = ref<TaskDetail[]>([]);
const selectedTasks = ref<TaskDetail[]>([]);
const loading = ref(false);
const summaryLoading = ref(false);
const cleanupLoading = ref(false);
const restartingTaskId = ref<string | null>(null);
const taskSummary = ref<TaskSummary>({
    total: 0,
    status: createEnumMap(DjangoTaskResultStatusOptions, 0),
});

const filters = ref({
    status: { value: null, matchMode: FilterMatchMode.EQUALS },
});

async function refreshSummary() {
    summaryLoading.value = true;
    await proxy.$axios.get<TaskSummary>('/api/common/tasksummary').then((response) => {
        taskSummary.value = response.data;
    }).catch(httpErrorNotification);
    summaryLoading.value = false;
}

async function refresh() {
    loading.value = true;
    await proxy.$axios.get<TaskDetail[]>('/api/common/tasks/detail').then((response) => {
        taskData.value = response.data;
    }).catch(httpErrorNotification);
    loading.value = false;
}

onMounted(refreshSummary);

async function cleanupExpiredTasks() {
    cleanupLoading.value = true;
    await proxy.$axios.post<number>('/api/common/tasks/cleanup').then(async () => {
        await refreshSummary();
    }).catch(httpErrorNotification);
    cleanupLoading.value = false;
}

function updateTaskSummary(status: DjangoTaskResultStatus, delta: number) {
    taskSummary.value.status[status] = Math.max(0, (taskSummary.value.status[status] ?? 0) + delta);
}

function addTask(task: TaskDetail) {
    taskData.value.unshift(task);
    taskSummary.value.total += 1;
    updateTaskSummary(task.status, 1);
}

function removeTask(taskId: string) {
    const index = taskData.value.findIndex((task) => task.id === taskId);
    if (index === -1) return;

    const [task] = taskData.value.splice(index, 1);
    selectedTasks.value = selectedTasks.value.filter((selectedTask) => selectedTask.id !== taskId);
    taskSummary.value.total = Math.max(0, taskSummary.value.total - 1);
    updateTaskSummary(task.status, -1);
}

async function restartTask(task: TaskDetail) {
    restartingTaskId.value = task.id;
    try {
        const response = await proxy.$axios.post<TaskDetail>('/api/common/tasks/restart', {
            task_id: task.id,
        });
        addTask(response.data);
    } catch (error) {
        httpErrorNotification(error);
    }
    restartingTaskId.value = null;
}

async function deleteSelected() {
    if (selectedTasks.value.length === 0) return;
    try {
        for (const task of selectedTasks.value) {
            await proxy.$axios.post('/api/common/tasks/delete', {
                task_id: task.id,
            });
            removeTask(task.id);
        }
    } catch (error) {
        httpErrorNotification(error);
    }
}
</script>
