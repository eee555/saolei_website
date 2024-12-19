<template>
    <el-text v-if="state == 'd'" type="warning">
        <LazyTooltip :content="t('common.state.d')" :hide-after="0" :show-after="500">
            <Warning />
        </LazyTooltip>
    </el-text>
    <el-text v-else-if="state == 'c'" type="success">
        <CircleCheck />
    </el-text>
    <el-icon v-else type="danger">
        <QuestionFilled />
    </el-icon>
</template>

<script setup lang="ts">

import { useI18n } from 'vue-i18n';
import LazyTooltip from './LazyTooltip.vue';

const data = defineProps({
    state: {
        type: String,
        default: "z",
    },
});

const { t } = useI18n();
</script>
