<template>
    <el-text tag="div" size="large">
        <ul>
            <li>
                {{ t('helper.saoleiImport.line_1') }}
            </li>
            <li>
                {{ t('helper.saoleiImport.line_2') }}
            </li>
            <li>
                {{ t('helper.saoleiImport.line_3') }}
            </li>
            <li>
                {{ t('helper.saoleiImport.line_4') }}
            </li>
        </ul>
    </el-text>
</template>

<script setup lang="ts">
import { ElText } from 'element-plus';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>
