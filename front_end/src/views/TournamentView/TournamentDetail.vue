<template>
    <!-- eslint-disable-next-line vue/no-v-html, vue/no-v-text-v-html-on-component -->
    <el-text v-if="tournament.name" tag="h1" v-html="tournament.name" />
    <!-- eslint-disable-next-line vue/no-v-html, vue/no-v-text-v-html-on-component -->
    <el-text v-if="tournament.description" v-html="tournament.getLocalDescription(local.language)" />
    <el-table v-if="data" :data="data" sortable>
        <el-table-column v-for="(value, key) in data[0]" :key="key" :label="key" :prop="key" />
    </el-table>
</template>

<script setup lang="ts">

import { Tournament } from '@/utils/tournaments';
import { ElText, ElTable, ElTableColumn } from 'element-plus';
import { local } from '@/store';

defineProps({
    tournament: {
        type: Tournament,
        default: () => new Tournament({}),
    },
    data: {
        type: Array as () => Record<string, any>[],
        default: () => [],
    },
});

</script>
