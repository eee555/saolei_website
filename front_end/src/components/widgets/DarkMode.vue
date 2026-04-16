<template>
    <el-radio-group v-model="store" size="small" style="vertical-align: middle;">
        <el-radio-button :label="t('light')" value="light" />
        <el-radio-button :label="t('auto')" value="auto" />
        <el-radio-button :label="t('dark')" value="dark" />
    </el-radio-group>
</template>

<script lang="ts" setup name="DarkMode">

import { useColorMode } from '@vueuse/core';
import { ElRadioButton, ElRadioGroup } from 'element-plus';
import { useI18n } from 'vue-i18n';

const { store } = useColorMode();

const i18nMessages = {
    'zh-cn': {
        auto: '自动',
        dark: '深色',
        light: '浅色',
    },
    'en': {
        auto: 'auto',
        dark: 'dark',
        light: 'light',
    },
};

const { t } = useI18n({
    messages: i18nMessages,
});

</script>
