<template>
    <span style="flex: 1" />
    <el-statistic class="stathead" :title="`${t('common.score.sum')} ${t('common.prop.time')}`" :value="sumTime" :precision="3" />
    <el-statistic class="stathead" :title="`${t('common.score.sum')} ${t('common.prop.bvs')}`" :value="sumBvs" :precision="3" />
    <el-statistic class="stathead" :title="`${t('common.score.sum')} ${t('common.prop.stnb')}`" :value="sumStnb" :precision="3" />
    <span style="flex: 1" />
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { ElStatistic } from 'element-plus';

const { t } = useI18n();

defineProps({
    sumTime: {
        type: Number,
        required: true,
    },
    sumBvs: {
        type: Number,
        required: true,
    },
    sumStnb: {
        type: Number,
        required: true,
    },
});

</script>

<style lang="less" scoped>
.stathead {
    width: 30%;
    min-width: 12em;
    text-align: center;
}
</style>
