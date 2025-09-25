<template>
    <!-- eslint-disable-next-line vue/no-v-html, vue/no-v-text-v-html-on-component -->
    <el-text v-if="name" tag="h1" v-html="name" />
    <!-- eslint-disable-next-line vue/no-v-html, vue/no-v-text-v-html-on-component -->
    <el-text v-if="description" v-html="description" />
    <el-table v-if="data" :data="data" sortable>
        <el-table-column v-for="(value, key) in data[0]" :key="key" :label="key" :prop="key" />
    </el-table>
</template>

<script setup lang="ts">

import { ElText, ElTable } from 'element-plus';

defineProps({
    id: {
        type: Number,
        required: true,
    },
    name: {
        type: String,
        default: '',
    },
    description: {
        type: String,
        default: '',
    },
    data: {
        type: Array,
        default: () => [],
    },
});



</script>
