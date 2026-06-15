<template>
    <span v-if="state == MS_State.Identifier" :title="t('common.state.d')">
        <el-icon>
            <base-icon-identifier style="color: var(--el-color-warning)" />
        </el-icon>
    </span>
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
import { BaseIconFrozen, BaseIconPending } from '@/components/common/icon';
import { MS_State } from '@/utils/ms_const';

defineProps({
    state: {
        type: String as PropType<MS_State>,
        required: true,
    },
});

const { t } = useI18n();
</script>
