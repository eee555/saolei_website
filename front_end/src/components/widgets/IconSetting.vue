<template>
    <Tippy interactive animate-fill arrow trigger="click" :append-to="'parent'">
        <ElLink underline="never">
            <BaseIconSetting />
        </ElLink>
        <template #content>
            <BaseCardNormal style="width: auto;">
                <slot />
            </BaseCardNormal>
        </template>
    </Tippy>
</template>

<script setup lang="ts">
import { ElLink } from 'element-plus';
import { Tippy } from 'vue-tippy';

import BaseCardNormal from '../common/BaseCardNormal.vue';

import { BaseIconSetting } from '@/components/common/icon';
</script>
