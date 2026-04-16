<template>
    <el-link :underline="underline" @click.stop="visible = true">
        <slot />
    </el-link>
    <el-dialog v-if="visible" :model-value="true" width="100%" align-center body-class="center" :show-close="false" append-to-body :z-index="zIndex" @closed="visible=false">
        <slot name="overlay" />
        <template #header>
            <h2 class="text-regular" style="justify-self: center;">
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
