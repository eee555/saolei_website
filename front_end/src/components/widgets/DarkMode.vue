<template>
    <el-radio-group v-model="store" size="small" style="vertical-align: middle;">
        <el-radio-button :label="t('setting.colorscheme.light')" value="light" />
        <el-radio-button :label="t('setting.colorscheme.auto')" value="auto" />
        <el-radio-button :label="t('setting.colorscheme.dark')" value="dark" />
    </el-radio-group>
</template>

<script lang="ts" setup name="DarkMode">

import { useI18n } from 'vue-i18n';
import { useColorMode } from '@vueuse/core';
import { ElRadioGroup, ElRadioButton } from 'element-plus';

const { t } = useI18n()
const { store } = useColorMode()

</script>
