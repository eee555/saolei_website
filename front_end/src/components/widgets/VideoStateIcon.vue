<template>
    <base-tooltip v-if="state == 'd'" :show-delay="500">
        <BaseIconIdentifier style="color: var(--el-color-warning)" />
        <template #content>
            <el-text v-t="'common.state.d'" />
        </template>
    </base-tooltip>
    <base-tooltip v-else-if="state == 'e'" :show-delay="500">
        <BaseIconExternal style="color: var(--el-color-warning)" />
        <template #content>
            <el-text v-t="'common.state.e'" />
        </template>
    </base-tooltip>
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
import BaseIconVerified from '@/components/common/BaseIconVerified.vue';
import BaseIconIdentifier from '@/components/common/BaseIconIdentifier.vue';
import BaseIconExternal from '@/components/common/BaseIconExternal.vue';
import BaseTooltip from '@/components/common/BaseTooltip.vue';

defineProps({
    state: {
        type: String,
        default: "z",
    },
});

const { t } = useI18n();
</script>
