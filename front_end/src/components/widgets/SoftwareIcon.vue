<template>
    <el-text v-if="software == 'a'">
        <img style="width: 16px; height: 16px" src="../../assets/img/ms_arbiter_MAINICON.ico"/>
    </el-text>
    <el-text v-else-if="software == 'e'">
        <img style="width: 16px; height: 16px" src="../../assets/img/img_meta.png"/>
    </el-text>
    <el-text v-else type="danger">
        <QuestionFilled style="width: 16px; height: 16px"/>
    </el-text>
</template>

<script setup lang="ts">
const data = defineProps({
    software: {
        type: String,
        default: "z",
    },
});
</script>
