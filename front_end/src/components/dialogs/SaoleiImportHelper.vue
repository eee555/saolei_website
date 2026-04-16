<template>
    <div class="text text-medium">
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
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>
