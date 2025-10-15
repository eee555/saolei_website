<template>
    <div class="cell">
        <el-text>{{ t(`common.level.short${level}`) }}</el-text>
    </div>
    <div v-for="i in count" class="cell">
        <el-text>{{ i }}</el-text>
    </div>
    <div class="cell">
        <el-text>{{ t('common.score.sum') }}</el-text>
    </div>
</template>

<script setup lang="ts">
import { MS_Level } from '@/utils/ms_const';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElText } from 'element-plus';

const { t } = useI18n();

defineProps({
    level: {
        type: String as PropType<MS_Level | ''>,
        default: '',
    },
    count: {
        type: Number,
        default: 0,
    },
});

</script>

<style lang="less" scoped>

@import './cell.less';

</style>
