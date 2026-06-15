<template>
    <ElLink :underline="underline" @click.stop="visible = true">
        <slot />
    </ElLink>
    <ElDialog v-if="visible" model-value width="100%" align-center body-class="center" :show-close="false" append-to-body :z-index="zIndex" @closed="visible=false">
        <slot name="overlay" />
        <template #header>
            <h2 class="text-regular" style="justify-self: center;">
                <slot name="header" />
            </h2>
        </template>
    </ElDialog>
</template>

<script lang="ts" setup>
import { ElDialog, ElLink } from 'element-plus';
import { PropType, ref } from 'vue';

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

const visible = ref(false);
</script>

<style scoped lang="less">
.el-dialog.center {
    justify-self: center;
    align-items: center;
    text-align: center;
}
</style>
