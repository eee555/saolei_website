<template>
    <span class="text-button" @click="centerDialogVisible = true;">友链</span>
    <el-dialog v-model="centerDialogVisible" title="友链" width="50%" align-center draggable :lock-scroll="false">
        <ul>
            <li><a target="_blank" href="https://gitee.com/ee55/saolei_website/issues">本站码云主页</a>
                <span>（反馈网站bug、提供建议、参与提案的讨论）</span>
            </li>
            <li><a target="_blank" href="https://github.com/eee555/saolei_website">本站Github主页</a>
                <span>（了解最新进展、加入开发团队、提供赞助）</span>
            </li>
            <li><a target="_blank" href="http://www.saolei.wang/">扫雷网</a>
                <span>（老牌的国内扫雷记录排名网站）</span>
            </li>
            <li><a target="_blank" href="https://minesweepergame.com/world-rankings.php">The Authoritative Minesweeper</a>
                <span>（老牌的国际扫雷记录排名网站）</span>
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
import { onMounted, ref, Ref } from 'vue'


const centerDialogVisible = ref(false);



onMounted(() => {


})







</script>


<style scoped>
a {
    color: blue;
}
</style>









