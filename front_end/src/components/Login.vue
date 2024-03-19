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
                    <el-input v-model.trim="valid_code" placeholder="验证码" prefix-icon="Key" class="code"></el-input>
                    &nbsp;
                    <ValidCode ref="refValidCode" :identifyCode="identifyCodeLog" />
                </div>
            </el-form-item>
            <el-form-item>
                <el-checkbox label="记住我" class="rememberMe" v-model="remember_me"></el-checkbox>
            </el-form-item>
            <el-form-item>
                <div style="color: red;">{{ hint_message }}</div>
            </el-form-item>
            <el-form-item>
                <el-button :disabled="(user_name && user_password && valid_code).length == 0"
                 type="primary" @click="login();">登录</el-button>
            </el-form-item>
            <div @click="login_visibile = false; retrieve_visibile = true; login_status = LoginStatus.IsRetrieve;"
                style="cursor: pointer;color: blue;">（找回密码）</div>
        </el-form>
    </el-dialog>
    <el-dialog v-model="register_visibile" title="用户注册" width="30%" draggable
        @close='() => { if (login_status !== LoginStatus.IsLogin) { login_status = LoginStatus.NotLogin; } }'>
        <el-form size="default">
            <el-form-item>
                <el-input v-model.trim="user_name_reg" placeholder="请输入用户昵称（唯一、登录凭证、无法修改）" prefix-icon="User"
                    maxlength="20" show-word-limit id="register_user_name_form"></el-input>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_email_reg" placeholder="请输入邮箱（唯一）" prefix-icon="Message" type="email"
                    id="register_email_form"></el-input>
            </el-form-item>
            <el-form-item>
                <div style="display: flex">
                    <el-input v-model.trim="valid_code_reg" placeholder="验证码" prefix-icon="Key" class="code"
                        maxlength="4"></el-input>
                    &nbsp;
                    <!-- <ValidCode2 :identifyCode="identifyCodeReg" ref="refValidCode2" /> -->
                    <ValidCode :identifyCode="identifyCodeReg" ref="refValidCode2" />
                    &nbsp;
                    <el-button link type="primary" @click="get_email_captcha('register')"
                        :disabled="valid_code_reg.length < 4">获取邮箱验证码</el-button>
                </div>
            </el-form-item>
            <el-form-item>
                <el-input v-model.trim="user_email_valid_code_reg" placeholder="请输入邮箱验证码" prefix-icon="Key"
                    maxlength="6" :disabled="valid_code_reg.length < 4" id="register_email_valid_code_form"></el-input>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_password_reg" placeholder="请输入6-20位密码" show-password prefix-icon="Lock"
                    minlength="6" maxlength="20" id="register_user_password_form"></el-input>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_password2_reg" placeholder="请输入确认密码" show-password prefix-icon="Lock"
                    minlength="6" maxlength="20"></el-input>
            </el-form-item>
            <el-checkbox v-model="checkout_user_agreement" name="checkoutSecret">已阅读并同意
                <a target="_blank" :href="AXIOS_BASE_URL + '/agreement.html'">新扫雷网用户协议</a>
            </el-checkbox>

            <el-form-item>
                <div style="color: red;">{{ hint_message }}</div>
            </el-form-item>
            <el-form-item>
                <el-button :disabled="(user_email_valid_code_reg && user_password_reg && user_password2_reg).length == 0"
                    type="primary" @click="register()">注册</el-button>
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
                    <!-- <ValidCode2 :identifyCode="identifyCodeReg" ref="refValidCode2" /> -->
                    <ValidCode :identifyCode="identifyCodeReg" ref="refValidCode2" />
                    &nbsp;
                    <el-button link type="primary" @click="get_email_captcha('retrieve')"
                        :disabled="valid_code_reg.length < 4">获取验证码</el-button>
                </div>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_email_valid_code_reg" placeholder="请输入邮箱验证码" prefix-icon="Key"
                    :disabled="valid_code_reg.length < 4" maxlength="6"></el-input>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_password_reg" placeholder="请输入新的6-20位密码" show-password prefix-icon="Lock"
                    minlength="6" maxlength="20"></el-input>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_password2_reg" placeholder="请输入确认密码" show-password prefix-icon="Lock"
                    minlength="6" maxlength="20"></el-input>
            </el-form-item>
            <el-form-item>
                <div style="color: red;">{{ hint_message }}</div>
            </el-form-item>
            <el-form-item>
                <el-button :disabled="(user_email_valid_code_reg && user_password_reg && user_password2_reg).length == 0"
                 type="primary" @click="retrieve()">确认修改密码</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>

<script lang="ts" setup>
// 注册、登录、找回密码的弹框及右上方按钮
import { onMounted, ref, Ref } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
import { LoginStatus } from "@/utils/common/structInterface"
import ValidCode from "@/components/ValidCode.vue";
// import ValidCode2 from "@/components/ValidCode2.vue";
import { genFileId, ElMessage } from 'element-plus'

const AXIOS_BASE_URL = process.env.VUE_APP_BASE_API;

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
// 登录对话框是否出现
const login_visibile = ref(false);
const register_visibile = ref(false);
const retrieve_visibile = ref(false);

const remember_me = ref(false);

const user_name = ref("");
const user_password = ref("");
const valid_code = ref("");

const identifyCodeLog = ref("");
const identifyCodeReg = ref("");
// const identifyCodes = ref("1234567890acdefjhijkmnprstuvwxyz");

const user_name_reg = ref("");
const user_email_reg = ref("");
// 图形验证码
const valid_code_reg = ref("");
// 邮箱验证码
const user_email_valid_code_reg = ref("");
const user_password_reg = ref("");
const user_password2_reg = ref("");

// 报错信息，在界面上显示
const hint_message = ref("");

// 是否同意用户协议
const checkout_user_agreement = ref(false);

let email_key = "";

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
    remember_me.value = false;
}

onMounted(() => {
    // console.log(document.cookie);
    login();
    window.onbeforeunload = function (e) {
        // 关闭网页时，删cookie。由于跨域问题，开发时，如开前后端各开一个服务器，
        // 体现不出效果，即：取消“记住我”，依然可以免密登录。部署以后，预期“记住我”的功能正常
        if (!remember_me.value) {
            let date = new Date();
            date.setDate(date.getDate() - 1);
            document.cookie = "session_id=;expires=" + date;
            var xhr = new XMLHttpRequest();
            xhr.open('POST', AXIOS_BASE_URL + '/userprofile/logout/', false);
            xhr.send(null);
            // 防止密码爆破，用户界面展示所有个人录像，进入其他人个人主页

        }
        return null;

    };
})


const login = () => {
    // 先用cookie尝试登录，可能登不上
    // 再用用户名密码
    var params = new URLSearchParams()
    const _id = localStorage.getItem("user_id");
    params.append('user_id', _id ? _id : "");
    params.append('username', user_name.value)
    params.append('password', user_password.value)
    if (valid_code.value) {
        params.append('captcha', valid_code.value)
        params.append('hashkey', refValidCode.value.hashkey)
    } else {
        params.append('captcha', "")
        params.append('hashkey', "")
    }

    proxy.$axios.post('/userprofile/login/',
        params,
    ).then(function (response) {
        if (response.data.status == 100) {
            hint_message.value = ""
            // console.log(response.data);
            // console.log(response.data.msg.name);

            user_name_show.value = response.data.msg.username;

            proxy.$store.commit('updateUser', response.data.msg);// 当前登录用户
            if (localStorage.getItem("player") === null) {
                // 解决刷新后改成用户自己
                localStorage.setItem("player", JSON.stringify(response.data.msg));
            }
            // proxy.$store.commit('updatePlayer', response.data.msg);// 看我的地盘看谁的
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
            hint_message.value = response.data.msg;
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
    // user_params.append('username', user_name_reg.value)
    user_params.append('password', user_password_reg.value);
    user_params.append('email', user_email_reg.value);
    user_params.append('email_key', email_key);
    user_params.append('email_captcha', user_email_valid_code_reg.value);
    proxy.$axios.post('/userprofile/retrieve/',
        user_params,
    ).then(function (response) {
        if (response.data.status == 100) {
            hint_message.value = "";
            user_name_show.value = response.data.msg;
            login_status.value = LoginStatus.IsLogin;
            emit('login'); // 向父组件发送消息
            retrieve_visibile.value = false;
            ElMessage.success('修改密码成功!')
        } else if (response.data.status >= 101) {
            hint_message.value = response.data.msg;
        }
    }).catch(function (error) { });
}

const register = () => {
    if (!user_name_reg.value) {
        hint_message.value = "请输入用户名！";
        return
    }
    if (!user_email_reg.value) {
        hint_message.value = "请输入邮箱！";
        return
    }
    if (user_email_valid_code_reg.value.length != 6) {
        hint_message.value = "请输入6位邮箱验证码！";
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
    if (!checkout_user_agreement.value) {
        hint_message.value = "请同意用户协议！";
        return
    }
    const email_form = document.getElementById('register_email_form') as HTMLInputElement;
    if (!email_form.checkValidity()) {
        hint_message.value = "邮箱格式不正确！";
        return
    }
    const user_name_form = document.getElementById('register_user_name_form') as HTMLInputElement;
    if (!user_name_form.checkValidity()) {
        // 不可能进来
        hint_message.value = "用户名格式不正确！长度不超过20位。";
        return
    }
    const email_valid_code_form = document.getElementById('register_email_valid_code_form') as HTMLInputElement;
    if (!email_valid_code_form.checkValidity()) {
        hint_message.value = "邮箱验证码格式不正确！请点击邮箱验证码并打开邮箱查收。";
        return
    }
    const user_password_form = document.getElementById('register_user_password_form') as HTMLInputElement;
    if (!user_password_form.checkValidity()) {
        hint_message.value = "密码格式不正确！长度应该为6-20位。";
        return
    }
    var user_params = new URLSearchParams()
    user_params.append('username', user_name_reg.value);
    user_params.append('password', user_password_reg.value);
    user_params.append('email', user_email_reg.value);
    user_params.append('email_key', email_key);
    user_params.append('email_captcha', user_email_valid_code_reg.value);
    proxy.$axios.post('/userprofile/register/',
        user_params,
    ).then(function (response) {
        // console.log(response.data);
        if (response.data.status == 100) {
            hint_message.value = ""
            user_name_show.value = user_name_reg.value;
            login_status.value = LoginStatus.IsLogin;
            proxy.$store.commit('updateUser', response.data.msg);// 当前登录用户
            // proxy.$store.commit('updatePlayer', response.data.msg);// 看我的地盘看谁的
            localStorage.setItem("player", JSON.stringify(response.data.msg));
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
            const player = proxy.$store.state.user;
            player.realname = "";
            emit('logout'); // 向父组件发送消息
            register_visibile.value = false;
            login_visibile.value = false;
            retrieve_visibile.value = false;
            // console.log(response);
        } else if (response.data.status >= 101) {
            // hint_message.value = response.data.msg;
            ElMessage.error('退出失败!')

        }
    }).catch(function (error) {
        // console.log("eee:" + error);
    });
}


const get_email_captcha = (type: string) => {
    if (!user_email_reg.value) {
        hint_message.value = "请输入邮箱！";
        return
    }
    var params = new URLSearchParams()
    params.append('captcha', valid_code_reg.value)
    params.append('hashkey', refValidCode2.value.hashkey)
    params.append('email', user_email_reg.value)
    params.append('type', type)
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
            email_key = response.data.hashkey;
            ElMessage.success('获取验证码成功，请至邮箱查看!')
            // console.log(response.data.hashkey);
            // console.log("注册成功");
        } else if (response.data.status > 100) {
            hint_message.value = "*" + response.data.msg;
            // console.log(refValidCode2);
            // console.log(refValidCode2.value);
            refValidCode2.value!.refreshPic();
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
