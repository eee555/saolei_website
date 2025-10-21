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
import { ElIcon, ElText } from 'element-plus';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseIconExternal from '@/components/common/BaseIconExternal.vue';
import BaseIconIdentifier from '@/components/common/BaseIconIdentifier.vue';
import BaseIconVerified from '@/components/common/BaseIconVerified.vue';
import BaseTooltip from '@/components/common/BaseTooltip.vue';
import { MS_State } from '@/utils/ms_const';

const { t } = useI18n();

defineProps({
    state: {
        type: String as PropType<MS_State>,
        required: true,
    },
});
</script>
