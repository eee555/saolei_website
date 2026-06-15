<template>
    <Tippy :delay="[showDelay, hideDelay]" :duration="[showAnimation, hideAnimation]" :follow-cursor="followCursor" placement="auto-start">
        <slot />
        <template #content>
            <ElCard class="card-small">
                <slot name="content" />
            </ElCard>
        </template>
    </Tippy>
</template>

<script setup lang="ts">
import { ElCard } from 'element-plus';
import { Tippy } from 'vue-tippy';

defineProps({
    showDelay: { type: Number, default: 0 },
    hideDelay: { type: Number, default: 0 },
    showAnimation: { type: Number, default: 300 },
    hideAnimation: { type: Number, default: 250 },
    followCursor: { type: Boolean, default: false },
});
</script>

<style lang="less" scoped>
.card-small {
  --el-card-padding: 5px;
}
</style>
