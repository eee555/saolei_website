<template>
    <el-dropdown @command="changeLanguage" trigger="click">
        <el-image :src="logo_lang" style="width: 24px; height: 24px; margin-top: 18px; cursor: pointer"></el-image>
        <template #dropdown>
            <el-dropdown-item v-for="item in options" :command="item.lang">
                {{ item.text }}
            </el-dropdown-item>
        </template>
    </el-dropdown>
</template>

<script lang="ts" setup name="LanguagePicker">
import { onBeforeMount } from "vue";
import i18n from "@/i18n";
import { useI18n } from "vue-i18n";
const t = useI18n();

import { useLocalStore } from "@/store";
const local = useLocalStore();

import logo_lang from "@/assets/language.svg";

const options = [
    { lang: "zh-cn", text: "简体中文" },
    { lang: "en", text: "English" },
    { lang: "de", text: "name" },
    { lang: "dev", text: "dev" },
];

onBeforeMount(() => {
    i18n.global.locale.value = local.language;
});

const changeLanguage = (value: any) => {
    i18n.global.locale.value = value;
    local.language = value;
};
</script>
