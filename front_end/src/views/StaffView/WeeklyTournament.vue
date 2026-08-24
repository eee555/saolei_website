<template>
    <ElForm label-width="120px">
        <ElFormItem label="比赛类型">
            <ElSelect v-model="tournamentFormat" style="width: 220px">
                <ElOption
                    v-for="option in tournamentFormatOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                />
            </ElSelect>
        </ElFormItem>
        <ElFormItem>
            <ElButton type="primary" :loading="creating" @click="createWeeklyTournament">
                创建下周打卡赛
            </ElButton>
        </ElFormItem>
    </ElForm>
    <ElDescriptions v-if="createdWeekly" title="创建结果" border :column="2">
        <ElDescriptionsItem label="比赛 ID">
            {{ createdWeekly.data.id }}
        </ElDescriptionsItem>
        <ElDescriptionsItem label="打卡赛">
            {{ createdWeekly.data.year }}W{{ createdWeekly.data.week }}
        </ElDescriptionsItem>
        <ElDescriptionsItem label="开始时间">
            {{ formatDateTime(createdWeekly.data.start_time) }}
        </ElDescriptionsItem>
        <ElDescriptionsItem label="结束时间">
            {{ formatDateTime(createdWeekly.data.end_time) }}
        </ElDescriptionsItem>
    </ElDescriptions>
</template>

<script setup lang="ts">
import { ElButton, ElDescriptions, ElDescriptionsItem, ElForm, ElFormItem, ElOption, ElSelect } from 'element-plus';
import { ref } from 'vue';

import { httpErrorNotification, successNotification } from '@/components/Notifications';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { toDate, toISODateTimeString } from '@/utils/datetime';

const { proxy } = useCurrentInstance();

const tournamentFormatOptions = [
    { label: '2高5中', value: 'c' },
] as const;

const tournamentFormat = ref(tournamentFormatOptions[0].value);
const creating = ref(false);
const createdWeekly = ref<WeeklyCreateResponse | null>(null);

interface WeeklyCreateResponse {
    data: {
        id: number;
        year: number;
        week: number;
        start_time: string;
        end_time: string;
        state: string;
        tournament_format: string;
    };
}

async function createWeeklyTournament() {
    creating.value = true;
    await proxy.$axios.post('/api/tournament/weekly/new', {
        tournament_format: tournamentFormat.value,
    }).then((response) => {
        createdWeekly.value = response.data;
        successNotification(response);
    }).catch(httpErrorNotification);
    creating.value = false;
}

function formatDateTime(value: string | Date | null | undefined) {
    const date = toDate(value);
    return date ? toISODateTimeString(date) : '';
}
</script>
