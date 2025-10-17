<template>
    <el-row style="height: 100%">
        <el-col :span="15">
            <el-table :data="data" table-layout="auto" sortable>
                <el-table-column v-for="prop in columns" :key="prop" :prop="prop" :label="prop" />
            </el-table>
        </el-col>
        <el-col :span="1" />
        <el-col :span="8">
            <el-button @click="calculate">计算所有选手成绩</el-button><br>
            <el-button @click="logList = []">清空日志</el-button><br>
            <el-button @click="award">计算排行并结束比赛</el-button><br>
            <el-text v-for="(log, index) in logList" :key="index" :style="{ display: 'block' }">
                {{ log }}
            </el-text>
        </el-col>
    </el-row>
</template>

<script setup lang="ts">
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { ref, watch } from 'vue';
import { httpErrorNotification, successNotification } from '@/components/Notifications';
import { ElButton, ElCol, ElTable, ElTableColumn, ElText, ElRow } from 'element-plus';
import { GSCParticipant } from '@/utils/gsc';
import { TournamentParticipant } from '@/utils/tournaments';

const { proxy } = useCurrentInstance();

const props = defineProps({
    id: {
        type: Number,
        default: 0,
    },
});

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
    }).catch((_error) => {
        logList.value.push('选手列表获取失败！');
    });
    for (const index in data.value) {
        const participant = data.value[index];
        if (participant.id === 0) continue;
        logList.value.push(`正在计算 ${participant.user__realname}#${participant.user__id} 的成绩...`);
        await proxy.$axios.post('tournament/gsc/refresh/', { id: participant.id }).then((response) => {
            data.value[index] = response.data;
            logList.value.push('计算完成！');
        }).catch((_error) => {
            logList.value.push('计算失败！');
        });
    }
}

function award() {
    if (props.id === 0) return;
    proxy.$axios.post('tournament/gsc/award/', { order: props.id }).then(successNotification).catch(httpErrorNotification);
}

</script>
