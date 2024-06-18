<template>
    <el-button v-if="store.login_status != LoginStatus.IsLogin" @click.stop="openLogin">
        {{ $t('menu.login') }}
    </el-button>
    <el-button v-if="store.login_status != LoginStatus.IsLogin" @click.stop="openRegister">
        {{ $t('menu.register') }}
    </el-button>
    <el-button v-if="store.login_status == LoginStatus.IsLogin" @click.stop="logout();">
        {{ $t('menu.logout') }}
    </el-button>
    <el-dialog v-model="login_visible" :title="$t('login.title')" width="30%" align-center draggable
        :lock-scroll="false" @close='closeLogin'>
        <el-form size="default">
            <el-form-item>
                <el-input v-model="user_name" :placeholder="$t('login.username')" prefix-icon="User"
                    maxlength="20"></el-input>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_password" :placeholder="$t('login.password')" maxlength="20" show-password
                    prefix-icon="Lock"></el-input>
            </el-form-item>
            <el-form-item>
                <div style="display: flex;">
                    <el-input v-model.trim="valid_code" :placeholder="$t('login.captcha')" prefix-icon="Key"
                        class="code"></el-input>
                    &nbsp;
                    <ValidCode ref="refValidCode" :identifyCode="identifyCodeLog" />
                </div>
            </el-form-item>
            <el-form-item>
                <el-checkbox :label="$t('login.keepMeLoggedIn')" class="rememberMe" v-model="remember_me"></el-checkbox>
            </el-form-item>
            <el-form-item>
                <div style="color: red;">{{ hint_message }}</div>
            </el-form-item>
            <el-form-item>
                <el-button :disabled="(user_name && user_password && valid_code).length == 0" type="primary"
                    @click="login();">{{ $t('login.confirm') }}</el-button>
            </el-form-item>
            <div @click="login_visible = false; retrieve_visible = true; store.login_status = LoginStatus.IsRetrieve;"
                style="cursor: pointer;color: blue;">{{ $t('login.forgetPassword') }}</div>
        </el-form>
    </el-dialog>
    <el-dialog v-model="register_visible" :title="$t('register.title')" width="30%" align-center draggable
        :lock-scroll="false" @close='closeLogin'>
        <el-form size="default">
            <el-form-item>
                <el-input v-model.trim="user_name_reg" :placeholder="$t('register.username')" prefix-icon="User"
                    maxlength="20" show-word-limit id="register_user_name_form"></el-input>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_email_reg" :placeholder="$t('register.email')" prefix-icon="Message"
                    type="email" id="register_email_form"></el-input>
            </el-form-item>
            <el-form-item>
                <div style="display: flex">
                    <el-input v-model.trim="valid_code_reg" :placeholder="$t('register.captcha')" prefix-icon="Key"
                        class="code" maxlength="4"></el-input>
                    &nbsp;
                    <!-- <ValidCode2 :identifyCode="identifyCodeReg" ref="refValidCode2" /> -->
                    <ValidCode :identifyCode="identifyCodeReg" ref="refValidCode2" />
                    &nbsp;
                    <el-button link type="primary" @click="get_email_captcha('register')"
                        :disabled="valid_code_reg.length < 4">{{ $t('register.getEmailCode') }}</el-button>
                </div>
            </el-form-item>
            <el-form-item>
                <el-input v-model.trim="user_email_valid_code_reg" :placeholder="$t('register.emailCode')"
                    prefix-icon="Key" maxlength="6" :disabled="valid_code_reg.length < 4"
                    id="register_email_valid_code_form"></el-input>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_password_reg" :placeholder="$t('register.password')" show-password
                    prefix-icon="Lock" minlength="6" maxlength="20" id="register_user_password_form"></el-input>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_password2_reg" :placeholder="$t('register.confirmPassword')" show-password
                    prefix-icon="Lock" minlength="6" maxlength="20"></el-input>
            </el-form-item>
            <el-checkbox v-model="checkout_user_agreement" name="checkoutSecret">{{ $t('register.agreeTo') }}
                <a target="_blank" :href="AXIOS_BASE_URL + '/agreement.html'">{{ $t('register.termsAndConditions')
                    }}</a>
            </el-checkbox>

            <el-form-item>
                <div style="color: red;">{{ hint_message }}</div>
            </el-form-item>
            <el-form-item>
                <el-button
                    :disabled="(user_email_valid_code_reg && user_password_reg && user_password2_reg).length == 0"
                    type="primary" @click="register()">{{ $t('register.confirm') }}</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
    <el-dialog v-model="retrieve_visible" :title="$t('forgetPassword.title')" width="30%" align-center draggable
        :lock-scroll="false" @close='closeLogin'>
        <el-form size="default">
            <el-form-item>
                <el-input v-model="user_email_reg" :placeholder="$t('forgetPassword.email')" prefix-icon="Message"
                    type="email"></el-input>
            </el-form-item>
            <el-form-item>
                <div style="display: flex">
                    <el-input v-model="valid_code_reg" :placeholder="$t('forgetPassword.captcha')" prefix-icon="Key"
                        class="code" maxlength="4"></el-input>
                    &nbsp;
                    <!-- <ValidCode2 :identifyCode="identifyCodeReg" ref="refValidCode2" /> -->
                    <ValidCode :identifyCode="identifyCodeReg" ref="refValidCode2" />
                    &nbsp;
                    <el-button link type="primary" @click="get_email_captcha('retrieve')"
                        :disabled="valid_code_reg.length < 4">{{ $t('forgetPassword.getEmailCode') }}</el-button>
                </div>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_email_valid_code_reg" :placeholder="$t('forgetPassword.emailCode')"
                    prefix-icon="Key" :disabled="valid_code_reg.length < 4" maxlength="6"></el-input>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_password_reg" :placeholder="$t('forgetPassword.password')" show-password
                    prefix-icon="Lock" minlength="6" maxlength="20"></el-input>
            </el-form-item>
            <el-form-item>
                <el-input v-model="user_password2_reg" :placeholder="$t('forgetPassword.confirmPassword')" show-password
                    prefix-icon="Lock" minlength="6" maxlength="20"></el-input>
            </el-form-item>
            <el-form-item>
                <div style="color: red;">{{ $t(hint_message) }}</div>
            </el-form-item>
            <el-form-item>
                <el-button
                    :disabled="(user_email_valid_code_reg && user_password_reg && user_password2_reg).length == 0"
                    type="primary" @click="retrieve()">{{ $t('forgetPassword.confirm') }}</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>

<script lang="ts" setup>
// 注册、登录、找回密码的弹框及右上方按钮
import { onMounted, ref, Ref, onBeforeMount, onUnmounted } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
import { LoginStatus } from "@/utils/common/structInterface"
import ValidCode from "@/components/ValidCode.vue";
import { genFileId, ElMessage } from 'element-plus'
import { useUserStore } from '../store'
const store = useUserStore()

import { useI18n } from 'vue-i18n';
const t = useI18n();

const AXIOS_BASE_URL = import.meta.env.VITE_BASE_API;

let refValidCode = ref<any>(null)
let refValidCode2 = ref<any>(null)


const user_name_show = ref(""); // 登录后右上方显示的用户名

// const login_status = ref(LoginStatus.NotLogin);
// 登录对话框是否出现
const login_visible = ref(false);
const register_visible = ref(false);
const retrieve_visible = ref(false);

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
    if (store.login_status == LoginStatus.Undefined) {
        login();
    } else if (store.login_status == LoginStatus.IsLogin) {
        // 解决改变窗口宽度，使得账号信息在显示和省略之间切换时，用户名不能显示的问题
        hint_message.value = ""
        user_name_show.value = store.user.username;
        if (store.user.is_banned) {
            user_name_show.value += "（您已被封禁，详情请询问管理员！）"
        }
        emit('login'); // 向父组件发送消息
        login_visible.value = false;
    }


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

const openLogin = () => {
    init_refvalues();
    store.login_status = LoginStatus.Login;
    login_visible.value = true;
    register_visible.value = false;
}

const openRegister = () => {
    init_refvalues();
    store.login_status = LoginStatus.Register;
    register_visible.value = true;
    login_visible.value = false;
}

const closeLogin = () => {
    if (store.login_status !== LoginStatus.IsLogin) {
        store.login_status = LoginStatus.NotLogin;
    }
}

const login = async () => {
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

    await proxy.$axios.post('/userprofile/login/',
        params,
    ).then(function (response) {
        if (response.data.status == 100) {
            hint_message.value = ""

            user_name_show.value = response.data.msg.username;

            store.user = response.data.msg;
            store.player = response.data.msg;
            if (response.data.msg.is_banned) {
                user_name_show.value += "（您已被封禁，详情请询问管理员！）"
            }
            store.login_status = LoginStatus.IsLogin;
            // mutations.updateLoginStatus(LoginStatus.IsLogin);
            // login_status.value = LoginStatus.IsLogin;
            emit('login'); // 向父组件发送消息
            login_visible.value = false;
            // console.log(response.data.msg);
            // if (!user_name.value) {
            //     // 如果本次是自动登录成功的，下次依然自动登录
            //     remember_me.value = true;
            // }
            // localStorage.setItem("user_id", response.data.id + "");
        } else if (response.data.status >= 101) {
            hint_message.value = response.data.msg;
            // console.log("登录失败");
            // console.log("*" + response.data);
            store.login_status = LoginStatus.NotLogin;
        }
    }).catch(() => {
        store.login_status = LoginStatus.NotLogin;
    })
}

const retrieve = () => {
    if (!user_email_reg.value) {
        hint_message.value = "common.msg.emptyEmail";
        return
    }
    if (!user_password_reg.value) {
        hint_message.value = "common.msg.emptyPassword";
        return
    }
    if (user_password_reg.value != user_password2_reg.value) {
        hint_message.value = "common.msg.confirmPasswordFail";
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
            // mutations.updateLoginStatus(LoginStatus.IsLogin);
            store.login_status = LoginStatus.IsLogin;
            // login_status.value = LoginStatus.IsLogin;
            store.user = response.data.msg;
            store.player = response.data.msg;
            emit('login'); // 向父组件发送消息
            retrieve_visible.value = false;
            ElMessage.success({ message: t.t('common.msg.forgetPassword.success'), offset: 68 });
        } else if (response.data.status >= 101) {
            hint_message.value = response.data.msg;
        }
    }).catch(function (error) { });
}

const register = () => {
    if (!user_name_reg.value) {
        hint_message.value = "common.msg.emptyUsername";
        return
    }
    if (!user_email_reg.value) {
        hint_message.value = "common.msg.emptyEmail";
        return
    }
    if (user_email_valid_code_reg.value.length != 6) {
        hint_message.value = "common.msg.emptyEmailCode";
        return
    }
    if (!user_password_reg.value) {
        hint_message.value = "common.msg.emptyPassword";
        return
    }
    if (user_password_reg.value != user_password2_reg.value) {
        hint_message.value = "common.msg.confirmPasswordFail";
        return
    }
    if (!checkout_user_agreement.value) {
        hint_message.value = "common.msg.agreeTAC";
        return
    }
    const email_form = document.getElementById('register_email_form') as HTMLInputElement;
    if (!email_form.checkValidity()) {
        hint_message.value = "common.msg.invalidEmail";
        return
    }
    const user_name_form = document.getElementById('register_user_name_form') as HTMLInputElement;
    if (!user_name_form.checkValidity()) {
        // 不可能进来
        hint_message.value = "common.msg.invalidUsername";
        return
    }
    const email_valid_code_form = document.getElementById('register_email_valid_code_form') as HTMLInputElement;
    if (!email_valid_code_form.checkValidity()) {
        hint_message.value = "common.msg.invalidEmailCode";
        return
    }
    const user_password_form = document.getElementById('register_user_password_form') as HTMLInputElement;
    if (!user_password_form.checkValidity()) {
        hint_message.value = "common.msg.invalidPassword";
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
            // login_status.value = LoginStatus.IsLogin;
            // mutations.updateLoginStatus(LoginStatus.IsLogin);
            store.login_status = LoginStatus.IsLogin;
            store.user = response.data.msg;
            store.player = response.data.msg;
            emit('login'); // 向父组件发送消息
            register_visible.value = false;
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
            // login_status.value = LoginStatus.NotLogin;
            // mutations.updateLoginStatus(LoginStatus.NotLogin);
            store.login_status = LoginStatus.NotLogin;
            // const player = store.user;
            store.user = {
                id: 0,
                username: "",
                realname: "",
                is_banned: false,
                country: ""
            };
            store.player = {
                id: 0,
                username: "",
                realname: "",
                is_banned: false,
                country: ""
            };
            emit('logout'); // 向父组件发送消息
            ElMessage.success({ message: t.t('common.msg.logoutSuccess'), offset: 68 });
            register_visible.value = false;
            login_visible.value = false;
            retrieve_visible.value = false;
        } else if (response.data.status >= 101) {
            ElMessage.error({ message: t.t('common.msg.logoutFail'), offset: 68 });
        }
    }).catch(function (error) {
        // console.log("eee:" + error);
    });
}


const get_email_captcha = (type: string) => {
    if (!user_email_reg.value) {
        hint_message.value = "common.msg.emptyEmail";
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
            ElMessage.success({ message: t.t('common.msg.emailCodeSent'), offset: 68 });
        } else if (response.data.status > 100) {
            hint_message.value = "*" + response.data.msg;
            refValidCode2.value!.refreshPic();
        }
    }).catch(function (error) {
        // console.log("eee:" + error);
    });
}


// defineExpose({
//     login_status,
// });


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
