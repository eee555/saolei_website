<template>
    <base-tooltip v-if="level == 'b'" :show-delay="500">
        <el-text size="small">
            {{ t('common.level.b') }}
        </el-text>
        <template #content>
            <el-text size="small">
                8x8/10
            </el-text>
        </template>
    </base-tooltip>
    <base-tooltip v-else-if="level == 'i'" :show-delay="500">
        <el-text size="small">
            {{ t('common.level.i') }}
        </el-text>
        <template #content>
            <el-text size="small">
                16x16/40
            </el-text>
        </template>
    </base-tooltip>
    <base-tooltip v-else-if="level == 'e'" :show-delay="500">
        <el-text size="small">
            {{ t('common.level.e') }}
        </el-text>
        <template #content>
            <el-text size="small">
                30x16/99
            </el-text>
        </template>
    </base-tooltip>
</template>

<script setup lang="ts">
import { ElText } from 'element-plus';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import BaseTooltip from '@/components/common/BaseTooltip.vue';
import { MS_Level } from '@/utils/ms_const';

const { t } = useI18n();

defineProps({
    level: {
        type: String as PropType<MS_Level>,
        required: true,
    },
});
</script>
