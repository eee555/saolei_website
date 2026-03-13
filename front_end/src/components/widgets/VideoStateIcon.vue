<template>
    <base-tooltip v-if="state == MS_State.Identifier" :show-delay="500">
        <el-icon>
            <base-icon-identifier style="color: var(--el-color-warning)" />
        </el-icon>
        <template #content>
            <el-text>{{ t('common.state.d') }}</el-text>
        </template>
    </base-tooltip>
    <el-text v-else-if="state == MS_State.Official" type="success">
        <el-icon>
            <base-icon-verified />
        </el-icon>
    </el-text>
    <el-text v-else-if="state == MS_State.Plain" type="info">
        <el-icon>
            <base-icon-pending />
        </el-icon>
    </el-text>
    <el-text v-else-if="state == MS_State.Frozen" type="danger">
        <el-icon>
            <base-icon-frozen />
        </el-icon>
    </el-text>
</template>

<script setup lang="ts">
import { ElIcon, ElText } from 'element-plus';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseIconIdentifier from '@/components/common/BaseIconIdentifier.vue';
import BaseIconVerified from '@/components/common/BaseIconVerified.vue';
import BaseTooltip from '@/components/common/BaseTooltip.vue';
import { BaseIconFrozen, BaseIconPending } from '@/components/common/icon';
import { MS_State } from '@/utils/ms_const';

const { t } = useI18n();

defineProps({
    state: {
        type: String as PropType<MS_State>,
        required: true,
    },
});
</script>
