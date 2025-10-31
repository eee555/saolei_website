<template>
    <base-tooltip :show-delay="500">
        <img style="width: 1em; height: 1em; vertical-align: -0.125em;" src="@/assets/img/ms_arbiter_MAINICON.ico">
        <template #content>
            <el-text>Minesweeper Arbiter</el-text>
        </template>
    </base-tooltip>
</template>

<script setup lang="ts">

import { ElText } from 'element-plus';

import BaseTooltip from './BaseTooltip.vue';

</script>
