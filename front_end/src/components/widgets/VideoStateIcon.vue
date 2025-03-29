<template>
    <base-tooltip v-if="state == 'd'" :show-delay="500">
        <BaseIconIdentifier style="color: var(--el-color-warning)" />
        <template #content>
            <el-text>{{ t('common.state.d') }}</el-text>
        </template>
    </base-tooltip>
    <base-tooltip v-else-if="state == 'e'" :show-delay="500">
        <BaseIconExternal style="color: var(--el-color-warning)" />
        <template #content>
            <el-text>{{ t('common.state.e') }}</el-text>
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
import { ElText, ElIcon } from 'element-plus';
import BaseIconVerified from '@/components/common/BaseIconVerified.vue';
import BaseIconIdentifier from '@/components/common/BaseIconIdentifier.vue';
import BaseIconExternal from '@/components/common/BaseIconExternal.vue';
import BaseTooltip from '@/components/common/BaseTooltip.vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

defineProps({
    state: {
        type: String,
        default: "z",
    },
});
</script>
