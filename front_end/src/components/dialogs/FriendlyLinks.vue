<template>
    <span class="text-button" @click="centerDialogVisible = true;">友链</span>
    <el-dialog v-model="centerDialogVisible" title="友链" width="50%" align-center draggable>
        <ul>
            <li><a href="https://github.com/eee555/saolei_website">本站主页</a></li>
            <li><a href="http://www.saolei.wang/">扫雷网</a></li>
            <li><a href="https://minesweepergame.com/world-rankings.php">The Authoritative Minesweeper（国际扫雷网）</a></li>
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
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
import { LoginStatus } from "@/utils/common/structInterface"
import { genFileId, ElMessage } from 'element-plus'



let refValidCode = ref<any>(null)
let refValidCode2 = ref<any>(null)

// enum LoginStatus {
//     IsLogin,
//     NotLogin,
//     Login,
//     Register
// }

const centerDialogVisible = ref(false);

const login_status = ref(LoginStatus.NotLogin);
const login_visibile = ref(false);
const register_visibile = ref(false);
const retrieve_visibile = ref(false);

const remember_me = ref(true);

const user_name = ref("");
const user_password = ref("");
const valid_code = ref("");

const identifyCodeLog = ref("");
const identifyCodeReg = ref("");
// const identifyCodes = ref("1234567890acdefjhijkmnprstuvwxyz");

const user_name_reg = ref("");
const user_email_reg = ref("");
const valid_code_reg = ref("");
const user_email_valid_code_reg = ref("");
const user_password_reg = ref("");
const user_password2_reg = ref("");

const hint_message = ref("");

const emit = defineEmits(['login', 'logout']);

onMounted(() => {


})


const user_login = () => {
    // 配合孙组件向爷组件传
    emit('login');
}

const user_logout = () => {
    // 配合孙组件向爷组件传
    emit('logout');
}



defineExpose({
    login_status,
});


</script>


<style>
.text-button {
    /* width: 12px; */
    display: inline-block
}

.text-button:hover {
    color: rgb(64, 158, 255);
    cursor: pointer;
}

input:invalid {
    outline: 2px solid rgb(167, 11, 11);
    border-radius: 3px;
}

.el-dialog .el-dialog__body {
    flex: 1;
    overflow: auto;
}
</style>









