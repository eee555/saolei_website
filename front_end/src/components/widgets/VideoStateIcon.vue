<template>
    <base-tooltip v-if="state == MS_State.Identifier" :show-delay="500">
        <el-icon>
            <base-icon-identifier style="color: var(--el-color-warning)" />
        </el-icon>
        <template #content>
            <span class="text">{{ t('common.state.d') }}</span>
        </template>
    </base-tooltip>
    <span v-else-if="state == MS_State.Official" class="text text-success">
        <el-icon>
            <base-icon-verified />
        </el-icon>
    </span>
    <span v-else-if="state == MS_State.Plain" class="text text-info">
        <el-icon>
            <base-icon-pending />
        </el-icon>
    </span>
    <span v-else-if="state == MS_State.Frozen" class="text text-danger">
        <el-icon>
            <base-icon-frozen />
        </el-icon>
    </span>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import { ElIcon } from 'element-plus';
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
