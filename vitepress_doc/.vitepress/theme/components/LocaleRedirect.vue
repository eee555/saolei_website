<script setup lang="ts">
import { onMounted } from 'vue';
import { withBase } from 'vitepress';

const localeStorageKey = 'openms-docs-locale';

function getPreferredLanguage() {
    const languages = navigator.languages?.length ? navigator.languages : [navigator.language];
    return languages[0]?.toLowerCase() ?? '';
}

onMounted(() => {
    const requestedLanguage = new URLSearchParams(window.location.search).get('lang');
    const hasRequestedLanguage = requestedLanguage === 'zh' || requestedLanguage === 'en';
    if (!hasRequestedLanguage && localStorage.getItem(localeStorageKey)) {
        return;
    }

    const preferredLanguage = hasRequestedLanguage ? requestedLanguage : getPreferredLanguage();
    if (preferredLanguage.startsWith('zh')) {
        localStorage.setItem(localeStorageKey, 'zh');
        return;
    }

    localStorage.setItem(localeStorageKey, 'en');
    window.location.replace(`${withBase('/en/')}${window.location.search}${window.location.hash}`);
});
</script>

<template>
    <span hidden />
</template>
