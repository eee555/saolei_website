<!-- el-tooltip 存在渲染性能问题 -->
<!-- Credit: https://www.cnblogs.com/zerofan/p/17282121.html -->
<!-- 注意：该组件受到全局设置 local.tooltip_show 影响 -->
<template>
    <el-tooltip v-if="local.tooltip_show && render" v-bind="$attrs" @mouseleave="render=false">
        <slot />
    </el-tooltip>
    <div v-else @mouseenter="render=local.tooltip_show"><slot/></div>
</template>

<script setup lang="ts">
import { ElTooltip } from 'element-plus';
import { local } from '@/store';
import { ref } from 'vue';

const render = ref<boolean>(false);

</script>