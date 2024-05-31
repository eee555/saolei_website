<template>
    <el-select v-model="i18n.global.locale.value" style="width: 100px">
        <el-option v-for="item in options" :key="item.lang" :label="item.text" :value="item.lang" />
    </el-select>
</template>

<script lang="ts" setup name="LanguagePicker">

import i18n from '@/i18n';
import { useI18n } from 'vue-i18n';
const t = useI18n();

const options = [
    { lang: 'dev', text: 'dev' },
    { lang: 'zh-cn', text: '简体中文' },
    { lang: 'de', text: 'name'},
    { lang: 'en', text: 'English'}
]

</script>