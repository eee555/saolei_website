<template>
    <span style="align-items: center;">
        <el-link data-cy="zoomout" :underline="false" :disabled="zoom <= 0.1" size="small" @click="zoom = zoom - 0.1">
            <BaseIconZoomOut />
        </el-link>
        <base-text-button data-cy="main" size="small" @wheel="handleTextWheel">&nbsp;{{ Math.round(zoom * 100).toString().padStart(3, '&ensp;') }}%&nbsp;</base-text-button>
        <el-link data-cy="zoomin" :underline="false" :disabled="zoom >= 4" size="small" @click="zoom = zoom + 0.1">
            <BaseIconZoomIn />
        </el-link>
    </span>
</template>

<script setup lang="ts">

import { ElLink } from 'element-plus';
import BaseIconZoomIn from '@/components/common/BaseIconZoomIn.vue';
import BaseIconZoomOut from '@/components/common/BaseIconZoomOut.vue';
import BaseTextButton from '@/components/common/BaseTextButton.vue';

const zoom = defineModel({ type: Number, default: 1 });

function handleTextWheel(event: WheelEvent) {
    event.preventDefault();
    zoom.value = Math.max(Math.min(zoom.value + event.deltaY * -0.001, 4), 0.1);
}

</script>

<style scoped lang="less">
</style>
