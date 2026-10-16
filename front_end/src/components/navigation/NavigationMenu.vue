<template>
    <nav ref="region" class="navigation-menu" :aria-label="label" @focusin="rememberFocus">
        <ElMenu
            ref="menu" mode="horizontal" :default-active="active" menu-trigger="click" ellipsis
            :ellipsis-icon="moreIcon"
            popper-class="site-navigation-popper" :popper-effect="local.darkmode ? 'dark' : 'light'"
            close-on-click-outside :show-timeout="0" :hide-timeout="0"
            @select="activate"
        >
            <NavigationEntry v-for="item in items" :key="item.id" :item="item" :active="active" @activate="activate" @navigate="navigated" />
        </ElMenu>
    </nav>
</template>

<script setup lang="ts">
import { useMutationObserver } from '@vueuse/core';
import type { MenuInstance } from 'element-plus';
import { ElMenu } from 'element-plus';
import type { PropType } from 'vue';
import { defineComponent, h, nextTick, onBeforeUnmount, useTemplateRef, watch } from 'vue';
import { useRouter } from 'vue-router';

import NavigationEntry from './NavigationEntry.vue';
import type { NavigationItem } from './types';

import { local } from '@/store';

const props = defineProps({
    items: { type: Array as PropType<NavigationItem[]>, required: true },
    active: { type: String, default: '' },
    label: { type: String, required: true },
    moreLabel: { type: String, required: true },
});
const emit = defineEmits<{ navigate: [] }>();
const router = useRouter();
const menu = useTemplateRef<MenuInstance>('menu');
const region = useTemplateRef<HTMLElement>('region');
let focusedControl: HTMLElement | undefined;
let focusedId: string | null = null;
const moreIcon = defineComponent(() => () => h('span', { class: 'navigation-more', 'aria-label': props.moreLabel }, [
    h('i', { class: 'pi pi-ellipsis-h', 'aria-hidden': 'true' }),
    h('span', { class: 'navigation-sr-only' }, props.moreLabel),
]));

function rememberFocus(event: FocusEvent) {
    if (!(event.target instanceof HTMLElement)) return;
    focusedControl = event.target;
    focusedId = event.target.closest('[data-navigation-id]')?.getAttribute('data-navigation-id') ?? null;
}

// ElMenu moves overflow items between parents; preserve keyboard focus when a node is remounted.
useMutationObserver(region, () => {
    if (!focusedControl || focusedControl.isConnected || document.activeElement !== document.body) return;
    void nextTick(() => {
        if (document.activeElement !== document.body) return;
        const replacement = [...region.value?.querySelectorAll<HTMLElement>('[data-navigation-id]') ?? []].
            find((item) => item.getAttribute('data-navigation-id') === focusedId && item.getClientRects().length > 0);
        const target = replacement?.querySelector<HTMLElement>('.navigation-control, .el-sub-menu__title')
            ?? region.value?.querySelector<HTMLElement>(':scope > .el-menu > .el-sub-menu:last-child > .el-sub-menu__title');
        focusedControl = undefined;
        target?.focus();
    });
}, { childList: true, subtree: true });

function close() {
    for (const item of props.items) menu.value?.close(item.id);
    menu.value?.close('sub-menu-more');
}

function findItem(id: string): NavigationItem | undefined {
    return props.items.flatMap((item) => [item, ...item.children ?? []]).find((item) => item.id === id);
}

function activate(id: string) {
    const item = findItem(id);
    if (!item) return;
    close();
    if (item.to !== undefined) void router.push(item.to);
    else if (item.href !== undefined) {
        if (item.target === '_blank') window.open(item.href, '_blank', 'noopener,noreferrer');
        else window.location.assign(item.href);
    } else void item.action?.();
    emit('navigate');
    void nextTick(() => menu.value?.updateActiveIndex(props.active));
}

function navigated() {
    close();
    emit('navigate');
}

watch(() => props.items, async () => {
    await nextTick();
    close();
    menu.value?.handleResize();
}, { deep: true, flush: 'post' });
onBeforeUnmount(close);
defineExpose({ close });
</script>
