<template>
    <div>
        <span class="text-button" v-show="login_status != LoginStatus.IsLogin"
            @click="init_refvalues(); login_status = LoginStatus.Login; login_visibile = true; register_visibile = false">
            登录
        </span>
        <div style="display:inline-block" v-show="login_status == LoginStatus.IsLogin">
            欢迎您，{{ user_name_show }}！
        </div>
        <span style="width:12px; display:inline-block">
        </span>|<span style="width:12px; display:inline-block">
        </span>
        <span class="text-button" v-show="login_status != LoginStatus.IsLogin"
            @click="init_refvalues(); login_status = LoginStatus.Register; register_visibile = true; login_visibile = false">
            注册
        </span>
        <span class="text-button" v-show="login_status == LoginStatus.IsLogin" @click="logout();">
            退出
        </span>
    </div>
    <el-dialog v-model="login_visibile" title="欢迎登录" width="30%" draggable
        @close='() => { if (login_status !== LoginStatus.IsLogin) { login_status = LoginStatus.NotLogin; } }'>
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
                <el-checkbox label="记住我" class="rememberMe" v-model="remember_me"></el-checkbox>
            </el-form-item>
            <el-form-item>
                <div style="color: red;">{{ hint_message }}</div>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="login();">登录</el-button>
            </el-form-item>
            <div @click="login_visibile = false; retrieve_visibile = true; login_status = LoginStatus.IsRetrieve;"
                style="cursor: pointer;color: blue;">（找回密码）</div>
        </el-form>
    </el-dialog>
    <el-dialog v-model="register_visibile" title="用户注册" width="30%" draggable
        @close='() => { if (login_status !== LoginStatus.IsLogin) { login_status = LoginStatus.NotLogin; } }'>
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
            <el-checkbox v-model="checkout_user_agreement" name="checkoutSecret">已阅读并同意
                <a :href="AXIOS_BASE_URL + '/agreement.html'">新扫雷网用户协议</a>
            </el-checkbox>

            <el-form-item>
                <div style="color: red;">{{ hint_message }}</div>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="register()">注册</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
    <el-dialog v-model="retrieve_visibile" title="找回密码" width="30%" draggable
        @close='() => { if (login_status !== LoginStatus.IsLogin) { login_status = LoginStatus.NotLogin; } }'>
        <el-form size="default">
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
                <el-input v-model="user_password_reg" placeholder="请输入新的6-20位密码" show-password prefix-icon="Lock"
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
                <el-button type="primary" @click="retrieve()">确认修改密码</el-button>
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
import { genFileId, ElMessage } from 'element-plus'
import { AXIOS_BASE_URL } from '../config';


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

// 报错信息，在界面上显示
const hint_message = ref("");

// 是否同意用户协议
const checkout_user_agreement = ref(false);

const emit = defineEmits(['login', 'logout']);

// 初始化，打开就删数据
const init_refvalues = () => {
    user_password.value = "";
    valid_code.value = "";
    user_name_reg.value = "";
    user_email_reg.value = "";
    valid_code_reg.value = "";
    user_email_valid_code_reg.value = "";
    user_password_reg.value = "";
    user_password2_reg.value = "";
    identifyCodeLog.value = "";
    identifyCodeReg.value = "";
    hint_message.value = "";
    user_name.value = "";
    checkout_user_agreement.value = false;
    remember_me.value = true;
}

onMounted(() => {
    // console.log(document.cookie);
    login();
    // window.onbeforeunload = function (e) {
    //     // 关闭网页时，删cookie。由于跨域问题，开发时，如开前后端各开一个服务器，
    //     // 体现不出效果，即：取消“记住我”，依然可以免密登录。部署以后，预期“记住我”的功能正常
    //     if (!remember_me.value) {
    //         let date = new Date();
    //         date.setDate(date.getDate() - 1);
    //         document.cookie = "session_id=;expires=" + date;
    //         var xhr = new XMLHttpRequest();
    //         xhr.open('POST', AXIOS_BASE_URL + '/userprofile/logout/', false);
    //         xhr.send(null);
    //         // 防止密码爆破，用户界面展示所有个人录像，进入其他人个人主页

    //     }
    //     return null;

    // };
})


const login = () => {
    // 先用cookie尝试登录，可能登不上
    // 再用用户名密码
    var params = new URLSearchParams()
    const _id = localStorage.getItem("user_id");
    params.append('user_id', _id ? _id : "");
    params.append('username', user_name.value)
    params.append('password', user_password.value)
    proxy.$axios.post('/userprofile/login/',
        params,
    ).then(function (response) {
        // console.log(response.data);
        // console.log(document.cookie.match("csrftoken"));
        // console.log(document.cookie);
        // console.log(user_name.value);
        // console.log(user_password.value);
        // console.log(response.headers);
        // console.log(response.config);
        if (response.data.status == 100) {
            hint_message.value = ""
            // console.log(response.data.msg);
            // console.log(response.data.msg.name);

            user_name_show.value = response.data.msg.username;

            proxy.$store.commit('updateUser', response.data.msg);// 当前登录用户
            proxy.$store.commit('updatePlayer', response.data.msg);// 看我的地盘看谁的
            if (response.data.msg.is_banned) {
                user_name_show.value += "（您已被封禁，详情请询问管理员！）"
            }
            login_status.value = LoginStatus.IsLogin;
            emit('login'); // 向父组件发送消息
            login_visibile.value = false;
            // console.log(response.data.msg);
            // if (!user_name.value) {
            //     // 如果本次是自动登录成功的，下次依然自动登录
            //     remember_me.value = true;
            // }
            localStorage.setItem("user_id", response.data.id + "");
        } else if (response.data.status >= 101) {
            // hint_message.value = response.data.msg;
            // console.log("登录失败");
            // console.log("*" + response.data);

        }
    })
}

const retrieve = () => {
    if (!user_email_reg.value) {
        hint_message.value = "请输入邮箱！";
        return
    }
    if (!user_password_reg.value) {
        hint_message.value = "请输入密码！";
        return
    }
    if (user_password_reg.value != user_password2_reg.value) {
        hint_message.value = "两次输入的密码不一致！";
        return
    }
    var user_params = new URLSearchParams()
    user_params.append('username', user_name_reg.value)
    user_params.append('password', user_password_reg.value)
    user_params.append('email', user_email_reg.value)
    user_params.append('usertoken', window.localStorage.getItem("usertoken") as string)
    user_params.append('email_captcha', user_email_valid_code_reg.value)
    proxy.$axios.post('/userprofile/retrieve/',
        user_params,
    ).then(function (response) {
        if (response.data.status == 100) {
            hint_message.value = ""
            user_name_show.value = user_name_reg.value;
            login_status.value = LoginStatus.IsLogin;
            emit('login'); // 向父组件发送消息
            retrieve_visibile.value = false;
        } else if (response.data.status >= 101) {
            hint_message.value = response.data.msg;
        }
    }).catch(function (error) { });
}

const register = () => {
    if (!checkout_user_agreement.value) {
        hint_message.value = "请同意用户协议！";
        return
    }
    if (!user_name_reg.value) {
        hint_message.value = "请输入用户名！";
        return
    }
    if (!user_email_reg.value) {
        hint_message.value = "请输入邮箱！";
        return
    }
    if (!user_password_reg.value) {
        hint_message.value = "请输入密码！";
        return
    }
    if (user_password_reg.value != user_password2_reg.value) {
        hint_message.value = "两次输入的密码不一致！";
        return
    }
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
            proxy.$store.commit('updateUser', response.data.msg);// 当前登录用户
            proxy.$store.commit('updatePlayer', response.data.msg);// 看我的地盘看谁的
            emit('login'); // 向父组件发送消息
            register_visibile.value = false;
            // console.log(response);
        } else if (response.data.status >= 101) {
            hint_message.value = response.data.msg;
            // console.log("注册失败");
            // console.log("*" + response.data);

        }
    }).catch(function (error) { });
}

const logout = async () => {
    proxy.$axios.post('/userprofile/logout/',
        {},
    ).then(function (response) {
        if (response.data.status == 100) {
            // hint_message.value = ""
            user_name_show.value = "";
            login_status.value = LoginStatus.NotLogin;
            emit('logout'); // 向父组件发送消息
            register_visibile.value = false;
            login_visibile.value = false;
            retrieve_visibile.value = false;
            // console.log(response);
        } else if (response.data.status >= 101) {
            // hint_message.value = response.data.msg;
            ElMessage.error('退出失败!')
            // console.log("退出失败");
            console.log("*" + response.data);

        }
    }).catch(function (error) {
        // console.log("eee:" + error);
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
            ElMessage.success('获取验证码成功，请至邮箱查看!')
            // console.log(response.data.hashkey);
            // console.log("注册成功");
        } else if (response.data.status > 100) {
            hint_message.value = "*" + response.data.msg;
            // console.log("注册失败");
            // console.log(response.data);
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
/* input:invalid {
    outline: 2px solid rgb(167, 11, 11);
    border-radius: 3px;
}

.el-dialog .el-dialog__body {
    flex: 1;
    overflow: auto;
} */
</style>









