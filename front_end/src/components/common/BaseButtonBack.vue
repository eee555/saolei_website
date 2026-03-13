<template>
    <el-button v-bind="$attrs">
        <base-icon-prev />
        {{ t('common.button.back') }}
    </el-button>
</template>

<script setup lang="ts">
import { ElButton } from 'element-plus';
import { useI18n } from 'vue-i18n';

import { BaseIconPrev } from './icon';

const { t } = useI18n();
</script>
