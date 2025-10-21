<template>
    <base-tooltip :show-delay="500">
        <img style="width: 16px; height: 16px" src="@/assets/img/ms_arbiter_MAINICON.ico">
        <template #content>
            <el-text>Minesweeper Arbiter</el-text>
        </template>
    </base-tooltip>
</template>

<script setup lang="ts">

import { ElText } from 'element-plus';

import BaseTooltip from './BaseTooltip.vue';

</script>
