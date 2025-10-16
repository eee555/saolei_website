<template>
    <BaseIconArbiter v-if="software == 'a'" />
    <BaseIconMetasweeper v-else-if="software == 'e'" />
    <BaseIconViennasweeper v-else-if="software == 'r'" />
    <BaseIconClone07 v-else-if="software == 'm'" />
    <el-text v-else type="danger">
        <base-icon-question />
    </el-text>
</template>

<script setup lang="ts">
import { ElText } from 'element-plus';
import BaseIconArbiter from '@/components/common/BaseIconArbiter.vue';
import BaseIconMetasweeper from '@/components/common/BaseIconMetasweeper.vue';
import BaseIconViennasweeper from '../common/BaseIconViennasweeper.vue';
import BaseIconClone07 from '../common/BaseIconClone07.vue';
import { MS_Software } from '@/utils/ms_const';
import { PropType } from 'vue';
import BaseIconQuestion from '@/components/common/BaseIconQuestion.vue';

defineProps({
    software: {
        type: String as PropType<MS_Software>,
        default: 'u',
    },
});
</script>
