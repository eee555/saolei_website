<template>
    <base-tooltip :show-delay="500">
        <img style="width: 16px; height: 16px" :src="local.vienna_logo_legacy ? ViennaIconLegacy : ViennaIconNew">
        <template #content>
            <el-text>Viennasweeper</el-text>
        </template>
    </base-tooltip>
</template>

<script setup lang="ts">

import { ElText } from 'element-plus';

import BaseTooltip from './BaseTooltip.vue';

import { local } from '@/store';
import { ViennaIconLegacy, ViennaIconNew } from '@/utils/assets';

</script>
