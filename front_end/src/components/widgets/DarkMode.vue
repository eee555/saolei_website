<template>
    <ElRadioGroup v-model="store" size="small" style="vertical-align: middle;">
        <ElRadioButton :label="t('local.light')" value="light" />
        <ElRadioButton :label="t('local.auto')" value="auto" />
        <ElRadioButton :label="t('local.dark')" value="dark" />
    </ElRadioGroup>
</template>

<script lang="ts" setup name="DarkMode">
import { useColorMode } from '@vueuse/core';
import { ElRadioButton, ElRadioGroup } from 'element-plus';
import { useI18n } from 'vue-i18n';

const { store } = useColorMode();

const i18nMessages = {
    'zh-cn': { local: {
        auto: '自动',
        dark: '深色',
        light: '浅色',
    } },
    en: { local: {
        auto: 'auto',
        dark: 'dark',
        light: 'light',
    } },
};

const { t } = useI18n({
    messages: i18nMessages,
});
</script>
