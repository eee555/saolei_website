<template>
    <el-text v-if="level == 'b'">
        <LazyTooltip content="8x8/10" :hide-after="0" :show-after="500">
            {{ $t('common.level.b') }}
        </LazyTooltip>
    </el-text>
    <el-text v-else-if="level == 'i'">
        <LazyTooltip content="16x16/40" :hide-after="0" :show-after="500">
            {{ $t('common.level.i') }}
        </LazyTooltip>
    </el-text>
    <el-text v-else-if="level == 'e'">
        <LazyTooltip content="30x16/99" :hide-after="0" :show-after="500">
            {{ $t('common.level.e') }}
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
    level: {
        type: String,
        default: "z",
    },
});

const t = useI18n();
</script>