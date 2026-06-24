<template>
    <ElButton v-bind="$attrs">
        {{ t('common.button.cancel') }}
    </ElButton>
</template>

<script setup lang="ts">
import { ElButton } from 'element-plus';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>
