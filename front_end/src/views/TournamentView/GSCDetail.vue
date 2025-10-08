<template>
    <h1>第{{ order }}届金羊杯
        <TournamentStateBadge :state="tournament.state" />
    </h1>
    比赛时间：
    <el-text>
        {{ tournament.displayStartTime() }}
        &nbsp;~&nbsp;
        {{ tournament.displayEndTime() }}
    </el-text>
    &nbsp;
    <br>
    在比赛期间上传（以服务器接收时间为准）的所有录像中，取成绩最好的20局初级（bv>=10）、12局中级（bv>=30）、5局高级（bv>=100），计算总成绩。
    <br>
    比赛标识：{{ token === '' ? '比赛开始后显示' : token }}
    <IconCopy :text="token" />
    <br>
    <h3>如何参赛</h3>
    <GSCTokenGuide v-model="personaltoken" :order="order" :token="token" />
    <template v-if="tournament.state === TournamentState.Ongoing">
        <h3>
            即时成绩&nbsp;
            <base-icon-refresh @click="refresh" />
        </h3>
        <GSCPersonalSummary v-if="personalresult !== null" :participant="personalresult" />
    </template>
    <template v-if="[TournamentState.Finished, TournamentState.Awarded].includes(tournament.state)">
        <h3>
            比赛结果
        </h3>
        <GSCAllSummary :data="result" />
    </template>
</template>

<script setup lang="ts">

import { httpErrorNotification } from '@/components/Notifications';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { Tournament } from '@/utils/tournaments';
import { ElText } from 'element-plus';
import { ref, watch } from 'vue';
import TournamentStateBadge from './TournamentStateBadge.vue';
import IconCopy from '@/components/widgets/IconCopy.vue';
import { store } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import { TournamentState } from '@/utils/ms_const';
import { GSCParticipant } from '@/utils/gsc';
import GSCPersonalSummary from './GSCPersonalSummary.vue';
import GSCTokenGuide from './GSCTokenGuide.vue';
import BaseIconRefresh from '@/components/common/BaseIconRefresh.vue';
import GSCAllSummary from './GSCAllSummary.vue';

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
const personaltoken = ref<string>('');
const personalresult = ref<GSCParticipant | null>(null);

function refresh() {
    proxy.$axios.get('tournament/gscinfo/', {
        params: {
            id: props.id,
        },
    }).then((response) => {
        tournament.value = new Tournament(response.data.data);
        order.value = response.data.data.order;
        token.value = response.data.data.token;

        if (tournament.value.state === TournamentState.Ongoing && store.login_status === LoginStatus.IsLogin) {
            result.value = [];
            personaltoken.value = response.data.results.token;
            personalresult.value = {
                user__id: store.user.id,
                user__realname: store.user.realname,
                bt1st: response.data.results.bt1st,
                bt20th: response.data.results.bt20th,
                bt20sum: response.data.results.bt20sum,
                it1st: response.data.results.it1st,
                it12th: response.data.results.it12th,
                it12sum: response.data.results.it12sum,
                et1st: response.data.results.et1st,
                et5th: response.data.results.et5th,
                et5sum: response.data.results.et5sum,
            };
        } else {
            personaltoken.value = '';
            personalresult.value = null;
            result.value = response.data.results;
        }
    }).catch(httpErrorNotification);
}

watch(() => props.id, refresh, { immediate: true });

</script>
