<template>
    <pr-toolbar>
        对于失败的任务，点击“FAILED”按钮可以在控制台输出报错。
        <template #start>
            <el-button @click="deleteSelected">
                删除选中任务
            </el-button>
        </template>
    </pr-toolbar>
    <pr-data-table
        v-model:filters="filters"
        v-model:selection="selectedTasks"
        :value="taskData"
        filter-display="menu"
        paginator
        :rows="10"
        paginator-template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown JumpToPageInput CurrentPageReport"
    >
        <pr-column selection-mode="multiple" />
        <pr-column field="id" header="id" />
        <pr-column field="status" header="status">
            <template #body="{ data }">
                <el-button v-if="data.status === 'FAILED'" @click="console.log(data.traceback)">
                    {{ data.status }}
                </el-button>
                <template v-else>
                    {{ data.status }}
                </template>
            </template>
            <template #filter="{ filterModel, filterCallback }">
                <pr-select v-model="filterModel.value" :options="[...DjangoTaskResultStatusOptions]" @change="filterCallback()" />
            </template>
        </pr-column>
        <pr-column field="enqueued_at" header="enqueued_at" sortable>
            <template #body="{ data }">
                {{ utc_to_local_format(data.enqueued_at) }}
            </template>
        </pr-column>
        <pr-column field="started_at" header="started_at" sortable>
            <template #body="{ data }">
                {{ utc_to_local_format(data.started_at) }}
            </template>
        </pr-column>
        <pr-column field="finished_at" header="finished_at" sortable>
            <template #body="{ data }">
                {{ utc_to_local_format(data.finished_at) }}
            </template>
        </pr-column>
        <pr-column field="args_kwargs" header="args_kwargs" />
        <pr-column field="priority" header="priority" sortable />
        <pr-column field="task_path" header="task_path" />
        <pr-column field="worker_ids" header="worker_ids" />
        <pr-column field="queue_name" header="queue_name" />
        <pr-column field="backend_name" header="backend_name" />
        <pr-column field="run_after" header="run_after" sortable>
            <template #body="{ data }">
                {{ utc_to_local_format(data.run_after) }}
            </template>
        </pr-column>
        <pr-column field="return_value" header="return_value" />
        <pr-column field="exception_class_path" header="exception_class_path" />
    </pr-data-table>
</template>

<script setup lang="ts">
import { FilterMatchMode } from '@primevue/core/api';
import { ElButton } from 'element-plus';
import PrColumn from 'primevue/column';
import PrDataTable from 'primevue/datatable';
import PrSelect from 'primevue/select';
import PrToolbar from 'primevue/toolbar';
import { onMounted, ref } from 'vue';

import { DjangoTaskResultStatus, DjangoTaskResultStatusOptions } from '@/utils/common/structInterface';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { utc_to_local_format } from '@/utils/system/tools';

interface TaskDetail {
    id: string;
    status: DjangoTaskResultStatus;
    enqueued_at: string;
    started_at: string;
    finished_at: string;
    args_kwargs: {
        args: any[];
        kwargs: any;
    };
    priority: number;
    task_path: string;
    worker_ids: string[];
    queue_name: string;
    backend_name: string;
    run_after: string;
    return_value: any;
    exception_class_path: string;
    traceback: string;
}

const { proxy } = useCurrentInstance();

const taskData = ref<TaskDetail[]>([]);
const selectedTasks = ref<TaskDetail[]>([]);

const filters = ref({
    status: { value: null, matchMode: FilterMatchMode.EQUALS },
});

async function refresh() {
    await proxy.$axios.get('/common/staff/taskdetail/').then((response) => {
        taskData.value = response.data;
    });
}

onMounted(refresh);

async function deleteSelected() {
    if (selectedTasks.value.length === 0) return;
    for (const task of selectedTasks.value) {
        await proxy.$axios.post('/common/staff/taskdelete/', {
            task_id: task.id,
        });
    }
    selectedTasks.value.splice(0, selectedTasks.value.length);
    refresh();
}

</script>

<style lang="less" scoped>
.card {
    background-color: black;
}

</style>
