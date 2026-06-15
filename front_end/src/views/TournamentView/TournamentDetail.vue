<template>
    <!-- eslint-disable-next-line vue/no-v-html, vue/no-v-text-v-html-on-component -->
    <h1 v-if="tournament.name" class="text" v-html="tournament.name" />
    <!-- eslint-disable-next-line vue/no-v-html, vue/no-v-text-v-html-on-component -->
    <h1 v-if="tournament.description" class="text" v-html="tournament.getLocalDescription(local.language)" />
    <ElTable v-if="data" :data="data" sortable>
        <ElTableColumn v-for="(value, key) in data[0]" :key="key" :label="key" :prop="key" />
    </ElTable>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ElTable, ElTableColumn } from 'element-plus';

import { local } from '@/store';
import { Tournament } from '@/utils/tournaments';

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
