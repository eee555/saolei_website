<template>
    <el-link :underline="underline" @click.stop="visible = true">
        <slot />
    </el-link>
    <el-dialog v-model="visible" width="100%" align-center body-class="center" :show-close="false" append-to-body :z-index="zIndex">
        <slot name="overlay" />
        <template #header>
            <h2 style="justify-self: center; color: var(--el-text-color-regular)">
                <slot name="header" />
            </h2>
        </template>
    </el-dialog>
</template>

<script lang="ts" setup>

import { ElDialog, ElLink } from 'element-plus';
import { PropType, ref } from 'vue';

const visible = ref(false);

defineProps({
    zIndex: {
        type: Number,
        default: undefined,
    },
    underline: {
        type: String as PropType<'hover' | 'always' | 'never'>,
        default: 'never',
    },
});

</script>

<style scoped lang="less">
.el-dialog.center {
    justify-self: center;
    align-items: center;
    text-align: center;
}
</style>
