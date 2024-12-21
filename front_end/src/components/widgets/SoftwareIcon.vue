<template>
    <el-text v-if="software == 'a'">
        <LazyTooltip content="Minesweeper Arbiter" :hide-after="0" :show-after="500">
            <img style="width: 16px; height: 16px" src="../../assets/img/ms_arbiter_MAINICON.ico"/>
        </LazyTooltip>
    </el-text>
    <el-text v-else-if="software == 'e'">
        <LazyTooltip :content="t('common.software.metasweeper')" :hide-after="0" :show-after="500">
            <img style="width: 16px; height: 16px" src="../../assets/img/img_meta.png"/>
        </LazyTooltip>
    </el-text>
    <el-text v-else type="danger">
        <QuestionFilled style="width: 16px; height: 16px"/>
    </el-text>
</template>

<script setup lang="ts">

import { useI18n } from 'vue-i18n';
import LazyTooltip from './LazyTooltip.vue';

const data = defineProps({
    software: {
        type: String,
        default: "z",
    },
});

const { t } = useI18n();
</script>
