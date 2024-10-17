<template>
    <el-button v-if="store.login_status != LoginStatus.IsLogin" @click.stop="login_visible = true" class="fakemenuitem"
        text size="small">
        {{ $t('menu.login') }}
    </el-button>
    <el-button v-if="store.login_status != LoginStatus.IsLogin" @click.stop="register_visible = true"
        style="margin-left: 0px;" class="fakemenuitem" text size="small">
        {{ $t('menu.register') }}
    </el-button>
    <el-button v-if="store.login_status == LoginStatus.IsLogin" @click.stop="logout();" class="fakemenuitem" text
        size="small">
        {{ $t('menu.logout') }}
    </el-button>
    <!-- 以下的所有表单的输入项都需要@keydown.stop，解决horizontal菜单截留空格操作的问题。 -->
    <!-- https://github.com/element-plus/element-plus/issues/10172#issuecomment-1295794523 -->
    <LoginDialog v-model="login_visible" @login="login"
        @forget-password="login_visible = false; retrieve_visible = true;" @keydown.stop />
    <RegisterDialog v-model="register_visible" @login="login" @keydown.stop />
    <RetrieveDialog v-model="retrieve_visible" @login="login" @keydown.stop />
</template>

<script lang="ts" setup>
// 注册、登录、找回密码的弹框及右上方按钮
import { onMounted, ref } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
import { LoginStatus } from "@/utils/common/structInterface"
import LoginDialog from "@/components/dialogs/LoginDialog.vue"
import RetrieveDialog from './dialogs/RetrieveDialog.vue';
import { ElMessage } from 'element-plus'
import { store, local } from '../store'

import { useI18n } from 'vue-i18n';
import { deepCopy } from '@/utils';
import RegisterDialog from './dialogs/RegisterDialog.vue';
import { httpErrorNotification } from './Notifications';
const t = useI18n();

// 登录对话框是否出现
const login_visible = ref(false);
const register_visible = ref(false);
const retrieve_visible = ref(false);

const remember_me = ref(true);

const emit = defineEmits(['login', 'logout']);

onMounted(() => {
    if (store.login_status == LoginStatus.Undefined) {
        login_auto();
    } else if (store.login_status == LoginStatus.IsLogin) {
        // 解决改变窗口宽度，使得账号信息在显示和省略之间切换时，用户名不能显示的问题
        emit('login'); // 向父组件发送消息
        login_visible.value = false;
    }

    window.onbeforeunload = function (e) {
        // 关闭网页时，假如没选记住我，就退出
        // 对于游客，此处不会发logout
        if (!remember_me.value) {
            logout();
        }
        return null;
    };
})

const login_auto = async () => {
    proxy.$axios.get('/userprofile/loginauto/').then(function (response) {
        if (response.data.id) {
            store.user = deepCopy(response.data); // 直接赋值会导致user和player共用一个字典！！
            store.player = deepCopy(response.data);
            store.login_status = LoginStatus.IsLogin;
        }
        else {
            store.login_status = LoginStatus.NotLogin;
        }
    })
}

const login = (user: any, remember: boolean) => {
    store.user = deepCopy(user);
    store.player = deepCopy(user);
    store.login_status = LoginStatus.IsLogin;
    login_visible.value = false;
    register_visible.value = false;
    remember_me.value = remember;
}

const logout = async () => {
    proxy.$axios.post('/userprofile/logout/',
        {},
    ).then(function (response) {
        // login_status.value = LoginStatus.NotLogin;
        // mutations.updateLoginStatus(LoginStatus.NotLogin);
        store.login_status = LoginStatus.NotLogin;
        // const player = store.user;
        store.user = {
            id: 0,
            username: "",
            realname: "",
            is_banned: false,
            is_staff: false,
            country: ""
        };
        emit('logout'); // 向父组件发送消息
        ElMessage.success({ message: t.t('common.msg.logoutSuccess'), offset: 68 });
        register_visible.value = false;
        login_visible.value = false;
        retrieve_visible.value = false;
    }).catch(httpErrorNotification);
}

</script>


<style lang="less" scoped>
.fakemenuitem {
    height: v-bind("local.menu_height + 'px'");
    font-size: v-bind("local.menu_font_size + 'px'"); // Somehow doesn't work
}
</style>
