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

watch(() => props.id, () => {
    if (props.id === 0) return;
    proxy.$axios.get('tournament/gsc/participants/', { params: { order: props.id } }).then((response) => {
        data.value = response.data.data;
    }).catch(httpErrorNotification);
});

async function calculate() {
    if (props.id === 0) return;
    logList.value.push('获取选手列表...');
    await proxy.$axios.get('tournament/gsc/participants/', { params: { order: props.id } }).then((response) => {
        data.value = response.data.data;
        logList.value.push(`选手列表获取完成，共${data.value.length}位选手`);
    }).catch(() => {
        logList.value.push('选手列表获取失败！');
    });
    for (const [index, participant] of data.value.entries()) {
        if (participant.id === 0) continue;
        logList.value.push(`正在计算 ${participant.user__realname}#${participant.user__id} 的成绩...`);
        await proxy.$axios.post('tournament/gsc/refresh/', { id: participant.id }).then((response) => {
            data.value[index] = response.data;
            logList.value.push('计算完成！');
        }).catch(() => {
            logList.value.push('计算失败！');
        });
    }
}

function award() {
    if (props.id === 0) return;
    proxy.$axios.post('tournament/gsc/award/', { order: props.id }).then(successNotification).catch(httpErrorNotification);
}
</script>
