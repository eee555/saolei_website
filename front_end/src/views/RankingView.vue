<template>
    <div>
        <el-container>
            <el-main style="background-color: white;padding: 1%;">
                <el-tabs type="border-card">
                    <el-tab-pane label="总排名">
                        排名 姓名 称号 初级 3BV/s 中级 3BV/s 高级 3BV/s 总计 3BV/s 升降
                    </el-tab-pane>
                    <el-tab-pane label="业余">业余</el-tab-pane>
                    <el-tab-pane label="职业">职业</el-tab-pane>
                    <el-tab-pane label="NF">NF</el-tab-pane>
                    <el-tab-pane label="无猜">无猜</el-tab-pane>
                    <el-tab-pane label="进步">进步</el-tab-pane>
                    <el-tab-pane label="地区">地区</el-tab-pane>
                </el-tabs>
            </el-main>
            <el-aside width="30%" style="background-color: white;padding: 1%;">
                <el-tabs type="border-card">
                    <el-tab-pane label="每日一星">每日一星</el-tab-pane>
                    <el-tab-pane label="站长统计">站长统计</el-tab-pane>
                    <el-tab-pane label="如何评选？">如何评选？</el-tab-pane>
                </el-tabs>
            </el-aside>
        </el-container>
    </div>
</template>
  
<script setup lang='ts'>
import { ref, reactive } from 'vue'

</script>

<style lang='less'>


</style>
  