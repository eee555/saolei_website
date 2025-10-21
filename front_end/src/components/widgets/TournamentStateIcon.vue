<template>
    <el-text :type="types[state]">
        {{ t(`tournament.state.${state}`) }}
    </el-text>
</template>

<script setup lang="ts">

import { ElText } from 'element-plus';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import { TournamentState } from '@/utils/ms_const';

defineProps({
    state: {
        type: String as PropType<TournamentState>,
        required: true,
    },
});

const { t } = useI18n();

const types = {
    [TournamentState.Pending]: 'primary',
    [TournamentState.Preparing]: 'warning',
    [TournamentState.Ongoing]: 'danger',
    [TournamentState.Finished]: 'success',
    [TournamentState.Awarded]: 'info',
    [TournamentState.Cancelled]: 'info',
} as const;

</script>
