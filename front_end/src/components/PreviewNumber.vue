<template>
    <ElLink v-if="props.id" underline="never" class="clickable" @click="preview(props.id);">
        {{ props.text }}
    </ElLink>
    <span v-else>--</span>
</template>

<script setup lang="ts" name="PreviewNumber">
// 某个数字或字符串，点击后预览
import { ElLink } from 'element-plus';

import { preview } from '@/utils/common/PlayerDialog';

const props = defineProps({
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
