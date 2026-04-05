<template>
    <base-tooltip :show-delay="500">
        <img style="width: 16px; height: 16px" :src="local.vienna_logo_legacy ? viennaLogoLegacy : viennaLogoNew">
        <template #content>
            <el-text>Viennasweeper</el-text>
        </template>
    </base-tooltip>
</template>

<script setup lang="ts">

import { ElText } from 'element-plus';

import BaseTooltip from './BaseTooltip.vue';

import viennaLogoLegacy from '@/assets/img/viennasweeper.ico';
import viennaLogoNew from '@/assets/img/vsweep_16x16_4bit.ico';
import { local } from '@/store';

</script>
