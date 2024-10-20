<template>
    <el-descriptions border>
        <el-descriptions-item label="id">{{ data.id }}</el-descriptions-item>
        <el-descriptions-item label="name">{{ data.name }}</el-descriptions-item>
        <el-descriptions-item label="update_time">{{ data.update_time }}</el-descriptions-item>
        <el-descriptions-item label="total_views">{{ data.total_views }}</el-descriptions-item>
        <el-descriptions-item label="bt">{{ ms_to_s(data.b_t_ms) }}</el-descriptions-item>
        <el-descriptions-item label="it">{{ ms_to_s(data.i_t_ms) }}</el-descriptions-item>
        <el-descriptions-item label="et">{{ ms_to_s(data.e_t_ms) }}</el-descriptions-item>
        <el-descriptions-item label="st">{{ ms_to_s(data.s_t_ms) }}</el-descriptions-item>
        <el-descriptions-item label="bb">{{ cs_to_s(data.b_b_cent) }}</el-descriptions-item>
        <el-descriptions-item label="ib">{{ cs_to_s(data.i_b_cent) }}</el-descriptions-item>
        <el-descriptions-item label="eb">{{ cs_to_s(data.e_b_cent) }}</el-descriptions-item>
        <el-descriptions-item label="sb">{{ cs_to_s(data.s_b_cent) }}</el-descriptions-item>
    </el-descriptions>
</template>

<script setup lang="ts">
import { cs_to_s, ms_to_s } from '@/utils';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { PropType } from 'vue';

defineProps({
    data: {
        type: Object as PropType<any>,
        default: {},
    }
})

const { proxy } = useCurrentInstance();

</script>