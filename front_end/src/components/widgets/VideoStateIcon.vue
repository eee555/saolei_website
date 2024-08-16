<template>
    <el-text v-if="state == 'd'" type="warning">
        <Warning />
    </el-text>
    <el-text v-else-if="state == 'c'" type="success">
        <CircleCheck />
    </el-text>
    <el-icon v-else type="error">
        <QuestionFilled />
    </el-icon>
</template>

<script setup lang="ts">
const data = defineProps({
    state: {
        type: String,
        default: "z",
    },
});
</script>
