<template>
    <ElRow style="height: 100%">
        <ElCol :span="15">
            <ElTable :data="data" table-layout="auto" sortable>
                <ElTableColumn v-for="prop in columns" :key="prop" :prop="prop" :label="prop" />
            </ElTable>
        </ElCol>
        <ElCol :span="1" />
        <ElCol :span="8">
            <ElButton @click="calculate">
                计算所有选手成绩
            </ElButton>
            <br>
            <ElButton @click="logList = []">
                清空日志
            </ElButton>
            <br>
            <ElButton @click="award">
                计算排行并结束比赛
            </ElButton>
            <br>
            <span v-for="(log, index) in logList" :key="index" class="text" :style="{ display: 'block' }">
                {{ log }}
            </span>
        </ElCol>
    </ElRow>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import { ElButton, ElCol, ElRow, ElTable, ElTableColumn } from 'element-plus';
import { ref, watch } from 'vue';

import { httpErrorNotification, successNotification } from '@/components/Notifications';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import type { GSCParticipant } from '@/utils/gsc';
import type { TournamentParticipant } from '@/utils/tournaments';

const props = defineProps({
    id: {
        type: Number,
        default: 0,
    },
});

const { proxy } = useCurrentInstance();

const columns = ['user__id', 'user__realname', 'bt1st', 'bt20th', 'bt20sum', 'it1st', 'it12th', 'it12sum', 'et1st', 'et5th', 'et5sum', 't37'];

const data = ref<(GSCParticipant | TournamentParticipant)[]>([]);
const logList = ref<string[]>([]);

interface TaskResponse {
    type: 'success';
    data: {
        task_id: string;
    };
}

watch(() => props.id, () => {
    if (props.id === 0) return;
    proxy.$axios.get('/api/tournament/gsc/participants', { params: { order: props.id } }).then((response) => {
        data.value = response.data.data;
    }).catch(httpErrorNotification);
});

function calculate() {
    if (props.id === 0) return;
    logList.value.push('正在创建成绩刷新后台任务...');
    proxy.$axios.post<TaskResponse>('/api/tournament/gsc/refreshscore', { order: props.id }).then((response) => {
        successNotification(response);
        logList.value.push(`后台任务已创建：${response.data.data.task_id}`);
    }).catch((error: unknown) => {
        logList.value.push('后台任务创建失败！');
        httpErrorNotification(error);
    });
}

function award() {
    if (props.id === 0) return;
    logList.value.push('正在创建比赛结束后台任务...');
    proxy.$axios.post<TaskResponse>('/api/tournament/gsc/award', { order: props.id }).then((response) => {
        successNotification(response);
        logList.value.push(`后台任务已创建：${response.data.data.task_id}`);
    }).catch((error: unknown) => {
        logList.value.push('后台任务创建失败！');
        httpErrorNotification(error);
    });
}
</script>
