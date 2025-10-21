<template>
    <el-link v-if="data.id" :underline="false" class="clickable" @click="preview(data.id);">
        {{ data.text }}
    </el-link>
    <span v-else>--</span>
</template>

<script setup lang="ts" name="PreviewNumber">
// 某个数字或字符串，点击后预览
import { ElLink } from 'element-plus';

import { preview } from '@/utils/common/PlayerDialog';

const data = defineProps({
    id: {
        type: Number,
        default: 0,
    },
    text: {
        type: [String, Number],
        default: '',
    },
});

</script>

<style lang="less" scoped></style>
