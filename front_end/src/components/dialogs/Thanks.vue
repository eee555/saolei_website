<template>
    <span class="text-button" @click="centerDialogVisible = true;">{{ $t('menu.team') }}</span>
    <el-dialog v-model="centerDialogVisible" title="团队" width="50%" align-center draggable :lock-scroll="false">
        <strong>站长</strong>
        <div>eee555</div>
        <strong>开发</strong>
        <div>eee555、putianyi889</div>
        <strong>赞助</strong>
        <div>putianyi889</div>
        <strong>策划</strong>
        <div>eee555、putianyi889、Pulsar</div>
        <strong>美工</strong>
        <div>eee555</div>
        <strong>测试</strong>
        <div>eee555、putianyi889、Pulsar、lc4337、冰糖雪梨、生命★是┗ 〓┛是☆什么、Arya</div>
        <strong>管理员</strong>
        <div>少年、GodnuX、auk ;-;</div>
        <strong>技术顾问</strong>
        <div>hgraceb</div>
        <strong>安全顾问</strong>
        <div>T0nyX1ang</div>


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
import { onMounted, ref, Ref } from 'vue'

import { useI18n } from 'vue-i18n';
const t = useI18n();

const centerDialogVisible = ref(false);

</script>


<style></style>
