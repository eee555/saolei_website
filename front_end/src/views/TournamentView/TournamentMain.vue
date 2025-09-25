<template>
    <el-tabs tab-position="left">
        <el-tab-pane v-for="tournament in tournament_list" :key="tournament.id" :label="tournament.name">
            {{ tournament.name }}
        </el-tab-pane>
    </el-tabs>
</template>

<script setup lang="ts">

import { ref } from 'vue';
import { Tournament } from '@/utils/tournaments';
import { ElTabs, ElTabPane } from 'element-plus';

const tournament_list = ref<Tournament[]>([]);

</script>
