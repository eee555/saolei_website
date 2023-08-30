<template>
    <div style="text-align: right;">

        <el-button plain style="border: 0;" v-show="login_status != LoginStatus.IsLogin"
            @click="login_status = LoginStatus.Login; login_visibile = true; register_visibile = false">
            登录
        </el-button>
        <div style="display:inline-block" v-show="login_status == LoginStatus.IsLogin">
            欢迎您，{{ user_name_show }}！
        </div>
        <span>|</span>
        <el-button plain style="border: 0;" v-show="login_status != LoginStatus.IsLogin"
            @click="login_status = LoginStatus.Register; register_visibile = true; login_visibile = false">
            注册
        </el-button>
        <el-button plain style="border: 0;" v-show="login_status == LoginStatus.IsLogin" @click="logout()">
            退出
        </el-button>
    </div>
    <el-dialog v-model="login_visibile" title="欢迎登录" width="30%" draggable>
        <el-form size="default">
            <el-form-item>
                <el-input v-model="user_name" placeholder="用户名" prefix-icon="User" maxlength="20"></el-input>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_password" placeholder="密码" maxlength="20" show-password
                    prefix-icon="Lock"></el-input>
            </el-form-item>
            <el-form-item>
                <div style="display: flex;">
                    <el-input v-model="valid_code" placeholder="验证码" prefix-icon="Key" class="code"></el-input>
                    &nbsp;
                    <ValidCode :identifyCode="identifyCodeLog" ref="refValidCode" />
                </div>
            </el-form-item>
            <el-form-item>
                <el-checkbox label="记住我" class="rememberMe"></el-checkbox>
            </el-form-item>
            <el-form-item>
                <div style="color: red;">{{ hint_message }}</div>
            </el-form-item>
            <el-form-item>
                <el-button type="primary"  @click="login()">登录</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
    <el-dialog v-model="register_visibile" title="用户注册" width="30%" draggable>
        <el-form size="default">
            <el-form-item>
                <el-input v-model="user_name_reg" placeholder="请输入用户昵称" prefix-icon="User" maxlength="20"
                    show-word-limit></el-input>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_email_reg" placeholder="请输入邮箱" prefix-icon="Message" type="email"></el-input>
            </el-form-item>
            <el-form-item>
                <div style="display: flex">
                    <el-input v-model="valid_code_reg" placeholder="验证码" prefix-icon="Key" class="code"
                        maxlength="4"></el-input>
                    &nbsp;
                    <ValidCode2 :identifyCode="identifyCodeReg" ref="refValidCode2" />
                    &nbsp;
                    <el-button link type="primary" @click="get_email_captcha()">获取验证码</el-button>
                </div>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_email_valid_code_reg" placeholder="请输入邮箱验证码" prefix-icon="Key"
                    maxlength="6"></el-input>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_password_reg" placeholder="请输入6-20位密码" show-password prefix-icon="Lock"
                    minlength="6" maxlength="20"></el-input>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_password2_reg" placeholder="请输入确认密码" show-password prefix-icon="Lock" minlength="6"
                    maxlength="20"></el-input>
            </el-form-item>
            <el-form-item>
                <div style="color: red;">{{ hint_message }}</div>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="register()">注册</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>
  
<script lang="ts" setup>
// 注册、登录的弹框及右上方按钮
import { onMounted, ref, Ref, defineEmits } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
import { LoginStatus } from "@/utils/common/structInterface"
import ValidCode from "@/components/ValidCode.vue";
import ValidCode2 from "@/components/ValidCode2.vue";
// import { v4 as uuidv4 } from 'uuid';
// import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';
// axios.defaults.headers['Content-Type'] = 'application/x-www-form-urlencoded';
// import type { AxiosRequestConfig, AxiosResponse,AxiosError  } from 'axios'
// console.log(uuidv4());

let refValidCode = ref<any>(null)
let refValidCode2 = ref<any>(null)

// enum LoginStatus {
//     IsLogin,
//     NotLogin,
//     Login,
//     Register
// }

const user_name_show = ref("") // 登录后右上方显示的用户名

const login_status = ref(LoginStatus.NotLogin)
const login_visibile = ref(false)
const register_visibile = ref(false)

const user_name = ref("")
const user_password = ref("")
const valid_code = ref("")

const identifyCodeLog = ref("");
const identifyCodeReg = ref("");
// const identifyCodes = ref("1234567890acdefjhijkmnprstuvwxyz");

const user_name_reg = ref("")
const user_email_reg = ref("")
const valid_code_reg = ref("")
const user_email_valid_code_reg = ref("")
const user_password_reg = ref("")
const user_password2_reg = ref("")

const hint_message = ref("")

const emit = defineEmits(['login', 'logout'])

onMounted(() => {
    // console.log(666);
    login();
})

const login = () => {
    // 先用cookie尝试登录，可能登不上
    // 再用用户名密码
    var params = new URLSearchParams()
    params.append('username', user_name.value)
    params.append('password', user_password.value)
    proxy.$axios.post('/userprofile/login/',
        params,
    ).then(function (response) {
        // console.log(response.data);
        // console.log(response.status);
        // console.log(response.statusText);
        // console.log(response.headers);
        // console.log(response.config);
        if (response.data.status == 100) {
            hint_message.value = ""
            // console.log(response.data.msg);
            // console.log(response.data.msg.name);
            
            user_name_show.value = response.data.msg.name;
            login_status.value = LoginStatus.IsLogin;
            emit('login'); // 向父组件发送消息
            register_visibile.value = false;
            login_visibile.value = false;
            proxy.$store.commit('updateUser',response.data.msg);// 当前登录用户
            proxy.$store.commit('updatePlayer',response.data.msg);// 看我的地盘看谁的
        } else if (response.data.status >= 101) {
            // hint_message.value = response.data.msg;
            console.log("登录失败");
            // console.log("*" + response.data);

        }
    })
}

// window.localStorage.setItem('user_token', "00000000000000000000000000000000")
const register = () => {
    var user_params = new URLSearchParams()
    user_params.append('username', user_name_reg.value)
    user_params.append('password', user_password_reg.value)
    user_params.append('email', user_email_reg.value)
    user_params.append('usertoken', window.localStorage.getItem("usertoken") as string)
    user_params.append('email_captcha', user_email_valid_code_reg.value)
    // user_params.append('usertoken', window.localStorage.getItem("user_token") as string)
    proxy.$axios.post('/userprofile/register/',
        user_params,
    ).then(function (response) {
        // console.log(response.data);
        // console.log(response.status);
        // console.log(response.statusText);
        // console.log(response.headers);
        // console.log(response.config);
        if (response.data.status == 100) {
            hint_message.value = ""
            user_name_show.value = user_name_reg.value;
            login_status.value = LoginStatus.IsLogin;
            emit('login'); // 向父组件发送消息
            register_visibile.value = false;
            console.log(response);
        } else if (response.data.status >= 101) {
            hint_message.value = response.data.msg;
            // console.log("注册失败");
            // console.log("*" + response.data);

        }
    }).catch(function (error) {
        console.log("eee:" + error);
    });
}

const logout = () => {
    proxy.$axios.post('/userprofile/logout/',
        {},
    ).then(function (response) {
        if (response.data.status == 100) {
            hint_message.value = ""
            user_name_show.value = "";
            login_status.value = LoginStatus.NotLogin;
            emit('logout'); // 向父组件发送消息
            register_visibile.value = false;
            login_visibile.value = false;
            console.log(response);
        } else if (response.data.status >= 101) {
            hint_message.value = response.data.msg;
            // console.log("退出失败");
            // console.log("*" + response.data);

        }
    }).catch(function (error) {
        console.log("eee:" + error);
    });
}


const get_email_captcha = () => {
    var params = new URLSearchParams()
    params.append('captcha', valid_code_reg.value)
    params.append('hashkey', refValidCode2.value.hashkey)
    params.append('email', user_email_reg.value)
    // console.log(params);
    proxy.$axios.post('/userprofile/get_email_captcha/',
        params,
    ).then(function (response) {
        // console.log(response.data);
        // console.log(response.status);
        // console.log(response.statusText);
        // console.log(response.headers);
        // console.log(response.config);
        if (response.data.status == 100) {
            hint_message.value = ""
            window.localStorage.setItem("usertoken", response.data.hashkey)
            console.log(response.data.hashkey);
            console.log("注册成功");
        } else if (response.data.status > 100) {
            hint_message.value = "*" + response.data.msg;
            console.log("注册失败");
            console.log(response.data);
        }
    }).catch(function (error) {
        console.log("eee:" + error);
    });
}


defineExpose({
    login_status,
});


</script>


<style>
input:invalid {
    outline: 2px solid rgb(167, 11, 11);
    border-radius: 3px;
}
</style>









