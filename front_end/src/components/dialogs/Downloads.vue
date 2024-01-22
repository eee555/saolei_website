<template>
    <span class="text-button" @click="centerDialogVisible = true;">软件下载</span>
    <el-dialog v-model="centerDialogVisible" title="软件下载" width="50%" align-center draggable>
        <ul>
            <li><a style="color: blue;" href="https://developer-oss.lanrar.com/file/?AGYAPgg5BjdVXFRsV2JQPFtkV29URgNkViUBZgY3AWlUOlNhDyEAIwg7U2ABJVYyBCwCKlR9CjsGL1ZhAHJRZgAuAC0IPAYiVSVUZFdqUD1bZFcNVGIDZVZsATYGaQE5VGxTNQ9lAGQIaVM8AXNWMQQtAjpUPwo7BjJWZgBvUWYANQBvCHMGIlVzVD9XMVBhWzNXYVQkAzFWaAEoBmgBOVR7UzAPZAAwCG9TYAEwVmMEPQIzVD4KaQY1VmUAalFlADcAMQhgBjNVO1RmV2VQaVs4V2FUPgMwVmMBMwZtAWZUMFMqDygAPQguUyMBIFYkBDsCdVRiCmwGPFZhAGlRaQA3AGEIZAZiVSVUdldqUDxbZFc0VDYDMFZmATcGbwE4VGFTMA9hAGAIaVMrAXtWcQQ4AmtUfAo1BjBWZwBsUWUAOABkCG0GY1U6VDZXJVAkW3FXJVQ2AzBWZwE+Bm8BOVRtUzMPawBmCGlTIwEgVj4ELgI6VDoKOgYzVn4AbVFpADMAeQhkBmtVOlQsVzJQZ1s1">元扫雷3.1.6</a>
            （元扫雷网官方扫雷软件，包含八种模式的无猜扫雷、第三代录像播放器）
            </li>
            <li><a style="color: blue;" href="http://www.saolei.wang/Download/Arbiter_0.52.3.zip">Arbiter 0.52.3</a>
            （同时受到国际网、中国扫雷网、元扫雷网认可的老牌扫雷软件）
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


<style>

</style>









