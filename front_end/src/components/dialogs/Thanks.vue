<template>
    <span class="text-button" @click="centerDialogVisible = true;">致谢</span>
    <el-dialog v-model="centerDialogVisible" title="致谢" width="50%" align-center draggable :lock-scroll="false">
        <h2>站长</h2>
        <span>eee555</span>
        <h2>开发</h2>
        <span>eee555</span>
        <h2>赞助</h2>
        <span>putianyi889</span>
        <h2>产品</h2>
        <span>putianyi889、Pulsar</span>
        <h2>美工</h2>
        <span>max_</span>
        <h2>测试</h2>
        <span>lc4337、冰糖雪梨、生命★是┗ 〓┛是☆什么、Arya</span>
        <h2>管理员</h2>
        <span>无</span>
        <h2>技术顾问</h2>
        <span>hgraceb</span>
        <h2>安全顾问</h2>
        <span>T0nyX1ang</span>


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


<style></style>









