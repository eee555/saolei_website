<template>
    <h1>第{{ order }}届金羊杯<TournamentStateBadge :state="tournament.state" /></h1>
    比赛时间：
    <el-text>
        {{ tournament.displayStartTime() }}
        &nbsp;~&nbsp;
        {{ tournament.displayEndTime() }}
    </el-text>
    &nbsp;
    <br>
    在比赛期间上传的所有录像中，取成绩最好的20局初级（bv>=10）、12局中级（bv>=30）、5局高级（bv>=100），计算总成绩。
    <br>
    比赛标识：{{ token === '' ? '比赛开始后显示' : token }} <!-- 增加复制按钮 -->
    <br>
    在元扫雷中，设置正确的比赛标识，上传录像时即可自动参赛。
</template>

<script setup lang="ts">

import { httpErrorNotification } from '@/components/Notifications';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { Tournament } from '@/utils/tournaments';
import { ElText } from 'element-plus';
import { ref, watch } from 'vue';
import BaseOverlay from '@/components/common/BaseOverlay.vue';
import TournamentStateBadge from './TournamentStateBadge.vue';

interface GSCParticipant {
    id: number;
    realname: string;
    bt1st: number;
    bt20th: number;
    bt20sum: number;
    it1st: number;
    it12th: number;
    it12sum: number;
    et1st: number;
    et5th: number;
    et5sum: number;
}

const props = defineProps({
    id: {
        type: Number,
        required: true,
    },
});

const { proxy } = useCurrentInstance();

const tournament = ref<Tournament>(new Tournament({}));
const order = ref<number>(0);
const token = ref<string>('');
const result = ref<GSCParticipant[]>([]);

watch(() => props.id, () => {
    proxy.$axios.get('tournament/gscinfo/', {
        params: {
            id: props.id,
        },
    }).then((response) => {
        tournament.value = new Tournament(response.data.data);
        order.value = response.data.data.order;
        token.value = response.data.data.token;
        result.value = response.data.result;
    }).catch(httpErrorNotification);
}, { immediate: true });

</script>
