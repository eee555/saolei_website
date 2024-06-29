<template>
    <el-dropdown @command="changeLanguage" trigger="click">
        <el-image :src="logo_lang" class="icon"></el-image>
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
    { lang: "pl", text: "polski"},
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

<style lang="less" scoped>
.icon {
    margin-top: v-bind("local.menu_height / 4 + 'px'");
    margin-bottom: v-bind("local.menu_height / 4 + 'px'");
    cursor: pointer;
}
</style>