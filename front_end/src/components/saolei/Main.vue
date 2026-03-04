<template>
    <div style="width: 100%; justify-content: center; display: flex">
        <el-button @click="$emit('enterHelp')">
            <el-result title="新人必读" sub-title="使用说明、常见问题及注意事项" icon="info" />
        </el-button>
        &nbsp;
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
        <el-button @click="$emit('enterQueue')">
            <el-result title="导入队列" sub-title="查询导入状态，以录像为单位管理导入任务">
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
import { Memo, Operation, Promotion } from '@element-plus/icons-vue';
import { ElButton, ElIcon, ElResult, ElText } from 'element-plus';

defineEmits(['enterAuto', 'enterHelp', 'enterQueue']);
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
