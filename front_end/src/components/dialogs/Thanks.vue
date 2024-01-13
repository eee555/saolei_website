<template>
    <span class="text-button" @click="centerDialogVisible = true;">致谢</span>
    <el-dialog v-model="centerDialogVisible" title="致谢" width="50%" align-center draggable>
        <h2>开发</h2>
        <span>wjn</span>
        <h2>测试</h2>
        <span>pty、lc、zxt、zwb、yht</span>
        <h2>产品</h2>
        <span>yht</span>
        <h2>赞助</h2>
        <span>pty</span>


        <template #footer>
            <span class="dialog-footer">
                <el-button type="primary" @click="centerDialogVisible = false">
                    确定
                </el-button>
            </span>
        </template>
    </el-dialog>
</template>
  
<script lang="ts" setup>
// 注册、登录的弹框及右上方按钮
import { onMounted, ref, Ref, defineEmits } from 'vue'


const centerDialogVisible = ref(false);



onMounted(() => {


})







</script>


<style>

</style>









