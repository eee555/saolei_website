<template>
    <VCodeBlock v-bind="$attrs" highlightjs :theme="local.darkmode ? 'stackoverflow-dark' : 'stackoverflow-light'" :css-path="codeThemeUrl">
        <template v-if="$slots.label" #label="slotProps">
            <slot name="label" v-bind="slotProps" />
        </template>
        <template v-if="$slots.tabs" #tabs="slotProps">
            <slot name="tabs" v-bind="slotProps" />
        </template>
        <template v-if="$slots.copyButton" #copyButton="slotProps">
            <slot name="copyButton" v-bind="slotProps" />
        </template>
    </VCodeBlock>
</template>

<script setup lang="ts">
import { VCodeBlock } from '@wdns/vue-code-block';
import darkCodeTheme from 'highlight.js/styles/stackoverflow-dark.css?inline';
import lightCodeTheme from 'highlight.js/styles/stackoverflow-light.css?inline';
import { computed } from 'vue';
import type { ComponentSlots } from 'vue-component-type-helpers';

import { local } from '@/store';

// VCodeBlock fetches CSS text; Vite's development CSS asset URLs serve JavaScript.
const codeThemeUrl = computed(() => `data:text/css;charset=utf-8,${encodeURIComponent(local.value.darkmode ? darkCodeTheme : lightCodeTheme)}`);

defineOptions({ inheritAttrs: false });
defineSlots<ComponentSlots<typeof VCodeBlock>>();
</script>
