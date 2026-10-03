<template>
    <BaseTextButton v-if="props.id" class="clickable" data-cy="preview-number" @click="preview(props.id);">
        {{ props.text }}
    </BaseTextButton>
    <span v-else>--</span>
</template>

<script setup lang="ts" name="PreviewNumber">
// 某个数字或字符串，点击后预览
import BaseTextButton from '@/components/common/BaseTextButton.vue';
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
