<template>
    <el-select v-model="i18n.global.locale.value" style="width: 200px">
        <el-option v-for="item in options" :key="item.lang" :label="item.text" :value="item.lang" />
    </el-select>
</template>

<script lang="ts" setup name="LanguagePicker">

import i18n from '@/i18n';

const options = [
    { lang: 'dev', text: 'dev' },
    { lang: 'zh-cn', text: '简体中文' },
]

</script>