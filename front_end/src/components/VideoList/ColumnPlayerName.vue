<template>
    <el-table-column min-width="80">
        <template #default="player">
            <PlayerName class="name" :user-id="+player.row.player_id" :user-name="player.row.player_name" />
        </template>
    </el-table-column>
</template>

<script setup lang="ts">

import { ElTableColumn } from 'element-plus';
import PlayerName from '@/components/PlayerName.vue';

</script>
