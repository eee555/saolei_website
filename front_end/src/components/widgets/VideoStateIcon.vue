<template>
    <el-text v-if="state == 'd'" type="warning">
        <LazyTooltip :content="t('common.state.d')" :hide-after="0" :show-after="500">
            <BaseIconIdentifier />
        </LazyTooltip>
    </el-text>
    <el-text v-else-if="state == 'e'" type="warning">
        <LazyTooltip :content="t('common.state.e')" :hide-after="0" :show-after="500">
            <BaseIconExternal />
        </LazyTooltip>
    </el-text>
    <el-text v-else-if="state == 'c'" type="success">
        <base-icon-verified />
    </el-text>
    <el-icon v-else type="danger">
        <QuestionFilled />
    </el-icon>
</template>

<script setup lang="ts">

import { useI18n } from 'vue-i18n';
import { ElText, ElIcon } from 'element-plus';
import LazyTooltip from './LazyTooltip.vue';
import BaseIconVerified from '@/components/common/BaseIconVerified.vue';
import BaseIconIdentifier from '@/components/common/BaseIconIdentifier.vue';
import BaseIconExternal from '@/components/common/BaseIconExternal.vue';

defineProps({
    state: {
        type: String,
        default: "z",
    },
});

const { t } = useI18n();
</script>
