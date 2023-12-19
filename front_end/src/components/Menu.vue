<template>
    <div style="float: right;">
        <div style="display: inline-flex;">
            <Login @login="user_login" @logout="user_logout"></Login>
        </div>
        <span style="width:12px; display:inline-block">
        </span>|<span style="width:12px; display:inline-block">
        </span>软件下载<span style="width:12px; display:inline-block">
        </span>|<span style="width:12px; display:inline-block">
        </span>友链<span style="width:12px; display:inline-block">
        </span>|<span style="width:12px; display:inline-block">
        </span>团队
    </div>
</template>
  
<script lang="ts" setup>
// 注册、登录的弹框及右上方按钮
import { onMounted, ref, Ref, defineEmits } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
import { LoginStatus } from "@/utils/common/structInterface"
import ValidCode from "@/components/ValidCode.vue";
import ValidCode2 from "@/components/ValidCode2.vue";
import { genFileId, ElMessage } from 'element-plus'
import { AXIOS_BASE_URL } from '../config';
import Login from "./Login.vue";


let refValidCode = ref<any>(null)
let refValidCode2 = ref<any>(null)

// enum LoginStatus {
//     IsLogin,
//     NotLogin,
//     Login,
//     Register
// }

const user_name_show = ref(""); // 登录后右上方显示的用户名

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
.click-word:hover{
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









