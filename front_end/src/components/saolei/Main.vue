<template>
    <div style="width: 100%; justify-content: center; display: flex">
        <el-button plain @click="$emit('enterAuto')">
            <el-result title="一键导入" sub-title="自动脚本导入全部录像，耗时较长，推荐首次导入时使用">
                <template #icon>
                    <el-text type="info">
                        <el-icon :size="64">
                            <Promotion />
                        </el-icon>
                    </el-text>
                </template>
            </el-result>
        </el-button>
        &nbsp;
        <el-button @click="$emit('enterPage')">
            <el-result title="按页读取" sub-title="将一页录像加入队列，推荐增量更新时使用">
                <template #icon>
                    <el-text type="info">
                        <el-icon :size="64">
                            <Memo />
                        </el-icon>
                    </el-text>
                </template>
            </el-result>
        </el-button>
        &nbsp;
        <el-button @click="$emit('enterQueue')">
            <el-result title="导入队列" sub-title="查询导入进度，逐个导入录像">
                <template #icon>
                    <el-text type="info">
                        <el-icon :size="64">
                            <Operation />
                        </el-icon>
                    </el-text>
                </template>
            </el-result>
        </el-button>
    </div>
</template>

<script setup lang="ts">
import { ElButton, ElIcon, ElResult, ElText } from 'element-plus';
import { Memo, Operation, Promotion } from '@element-plus/icons-vue';

defineEmits(['enterAuto', 'enterPage', 'enterQueue']);
</script>

<style lang="less" scoped>
.el-button {
    width: 15em;
    height: 20em;
    display: inline-block;
}

.el-result {
    white-space: normal;
}
</style>
