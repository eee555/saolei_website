<template>
    <el-link v-if="data.id" :underline="false" @click="preview(data.id);" class="clickable">{{ data.text }}</el-link>
    <span v-else>--</span>
</template>

<script setup lang="ts" name="PreviewNumber">
// 某个数字或字符串，点击后预览
import { preview } from '@/utils/common/PlayerDialog';

const data = defineProps({
    id: {
        type: Number,
    },
    text: {
        type: [String, Number],
    },
})

</script>

<style lang="less" scoped></style>