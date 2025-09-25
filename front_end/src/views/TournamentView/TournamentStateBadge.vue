<template>
    <el-text v-if="state === TournamentState.Pending" type="primary">
        审核中
    </el-text>
    <el-text v-else-if="state === TournamentState.Preparing" type="warning">
        未开始
    </el-text>
    <el-text v-else-if="state === TournamentState.Ongoing" type="danger">
        进行中
    </el-text>
    <el-text v-else-if="state === TournamentState.Finished" type="success">
        结算中
    </el-text>
    <el-text v-else-if="state === TournamentState.Awarded" type="info">
        已结束
    </el-text>
    <el-text v-else>
        ???
    </el-text>
</template>

<script setup lang="ts">

import { ElText } from 'element-plus';
import { TournamentState } from '@/utils/ms_const';
import { PropType } from 'vue';

defineProps({
    state: {
        type: String as PropType<TournamentState>,
        required: true,
    },
});

</script>
