<template>
    <el-button v-bind="$attrs">
        {{ t('common.button.cancel') }}
    </el-button>
</template>

<script setup lang="ts">
import { ElButton } from 'element-plus';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>
