<template>
    <span class="text-button" @click="centerDialogVisible = true;">软件下载</span>
    <el-dialog v-model="centerDialogVisible" title="软件下载" width="50%" align-center draggable :lock-scroll="false">
        <ul>
            <li><a style="color: blue;" target="_blank" href="https://eee555.lanzn.com/iCNsT1a7qiqj">元扫雷3.1.6</a>
                （元扫雷网官方扫雷软件，包含八种模式的无猜扫雷、第三代录像播放器、自带光学识别求解器。）
            </li>
            <li><a style="color: blue;" href="http://www.saolei.wang/Download/Arbiter_0.52.3.zip">Arbiter 0.52.3</a>
                （同时受到国际网、中国扫雷网、元扫雷网认可的老牌扫雷软件，只有标准模式。）
            </li>

        </ul>

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









