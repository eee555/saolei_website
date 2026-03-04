<template>
    <el-text v-if="state == SaoleiVideoImportState.NOTPLANNED">
        未导入
    </el-text>
    <el-text v-else-if="state == SaoleiVideoImportState.IMPORTING">
        导入中
    </el-text>
    <el-text v-else-if="state == SaoleiVideoImportState.FAILED">
        导入失败
    </el-text>
    <el-text v-else-if="state == SaoleiVideoImportState.IMPORTED">
        已导入
    </el-text>
</template>

<script setup lang="ts">
import { ElText } from 'element-plus';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';

import { SaoleiVideoImportState } from './utils';

const { t } = useI18n();

defineProps({
    state: {
        type: String as PropType<SaoleiVideoImportState>,
        required: true,
    },
});
</script>
