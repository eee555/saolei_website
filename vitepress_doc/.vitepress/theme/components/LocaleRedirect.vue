<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useData, withBase } from 'vitepress';

const { page, theme, hash } = useData();
const path = computed(() => page.value.relativePath.replace(/^(zh|en)\//, '').replace(/(^|\/)index\.md$/, '$1').replace(/\.md$/, ''));
const locales = computed(() => (['zh', 'en'] as const).filter((locale) => theme.value.localizedPages[locale].includes(path.value)));
const missingLocale = computed(() => /^(zh|en)\//.exec(page.value.relativePath)?.[1]);
const suffix = ref('');

onMounted(() => {
    watch([page, hash], () => {
        suffix.value = window.location.search + window.location.hash;
    }, { immediate: true });
});
</script>

<template>
    <div class="locale-page vp-doc">
        <template v-if="missingLocale">
            <h1>{{ missingLocale === 'zh' ? '此页面暂无中文版本' : 'This page is not available in English.' }}</h1>
            <p>{{ missingLocale === 'zh' ? '可使用以下语言阅读此页面：' : 'You can read this page in:' }}</p>
        </template>
        <p v-else>正在根据浏览器语言跳转…… / Redirecting to your browser language…</p>
        <ul>
            <li v-for="locale in locales" :key="locale"><a :href="withBase(`/${locale}/${path}${suffix}`)">{{ locale === 'zh' ? '简体中文' : 'English' }}</a></li>
        </ul>
    </div>
</template>

<style scoped>
.locale-page {
    max-width: 720px;
    margin: 0 auto;
    padding: 32px 24px;
}
</style>
