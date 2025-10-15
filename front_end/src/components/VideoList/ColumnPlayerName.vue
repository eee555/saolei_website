<template>
    <el-table-column min-width="80">
        <template #default="{row}: {row: VideoAbstract}">
            <PlayerName class="name" :user-id="row.player_id" :user-name="row.player_name" />
        </template>
    </el-table-column>
</template>

<script setup lang="ts">

import { ElTableColumn } from 'element-plus';
import PlayerName from '@/components/PlayerName.vue';
import { VideoAbstract } from '@/utils/videoabstract';

</script>
