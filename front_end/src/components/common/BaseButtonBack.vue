<template>
    <ElButton v-bind="$attrs">
        <BaseIconPrev />
        {{ t('common.button.back') }}
    </ElButton>
</template>

<script setup lang="ts">
import { ElButton } from 'element-plus';
import { useI18n } from 'vue-i18n';

import { BaseIconPrev } from './icon';

const { t } = useI18n();
</script>
