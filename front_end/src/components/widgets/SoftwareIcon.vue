<template>
    <BaseIconArbiter v-if="software == 'a'" />
    <BaseIconMetasweeper v-else-if="software == 'e'" />
    <BaseIconViennasweeper v-else-if="software == 'r'" />
    <BaseIconClone07 v-else-if="software == 'm'" />
    <el-text v-else type="danger">
        <QuestionFilled style="width: 16px; height: 16px" />
    </el-text>
</template>

<script setup lang="ts">
import { ElText } from 'element-plus';
import BaseIconArbiter from '@/components/common/BaseIconArbiter.vue';
import BaseIconMetasweeper from '@/components/common/BaseIconMetasweeper.vue';
import BaseIconViennasweeper from '../common/BaseIconViennasweeper.vue';
import BaseIconClone07 from '../common/BaseIconClone07.vue';

defineProps({
    software: {
        type: String,
        default: 'z',
    },
});
</script>
