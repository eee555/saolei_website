<template>
    <div style="font-size: 30px;margin-top: 10px;">
        {{ store.player.username }}
        <span style="font-size: 18px; color: #555;">id: {{ store.player.id }}</span>
    </div>
    <div style="font-size: 16px;margin-bottom: 12px;color: #555;">
        {{ store.player.realname }}
    </div>
    <div style="overflow: auto ;font-size: 16px;margin-bottom: 12px;text-align: justify;">
        {{ store.player.signature }}
    </div>
    <el-button v-if="store.isSelf" @click="emit('edit')">
        修改信息
    </el-button>
</template>

<script setup lang="ts">

import { ElButton } from 'element-plus';

import { store } from '@/store';

const emit = defineEmits(['edit']);

</script>
