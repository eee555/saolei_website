<template>
    <el-text v-if="platform=='a'">
        Authoritative Minesweeper
    </el-text>
    <el-link v-else-if="platform=='c'" href="http://saolei.wang/" target="_blank" style="vertical-align: bottom;">
        扫雷网
    </el-link>
    <el-text v-else-if="platform=='g'">
        Minesweeper GO
    </el-text>
    <el-text v-else-if="platform=='l'">
        扫雷联萌
    </el-text>
    <el-text v-else-if="platform=='s'">
        Scoreganizer
    </el-text>
    <el-text v-else-if="platform=='w'">
        Minesweeper Online
    </el-text>
</template>

<script setup lang="ts">
const data = defineProps({
    platform: {
        type: String,
        default: "",
    },
});
</script>