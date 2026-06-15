<template>
    <el-button
        v-if="store.login_status != LoginStatus.IsLogin" class="fakemenuitem"
        text size="small" @click.stop="activeDialog = 'login'; dialogVisible = true"
    >
        {{ t('local.menu.login') }}
    </el-button>
    <el-button
        v-if="store.login_status != LoginStatus.IsLogin"
        style="margin-left: 0px;" class="fakemenuitem" text size="small" @click.stop="activeDialog = 'register'; dialogVisible = true"
    >
        {{ t('local.menu.register') }}
    </el-button>
    <el-button
        v-if="store.login_status == LoginStatus.IsLogin" class="fakemenuitem" text
        size="small" @click.stop="logout();"
    >
        {{ t('local.menu.logout') }}
    </el-button>
    <!-- 以下的所有表单的输入项都需要@keydown.stop，解决horizontal菜单截留空格操作的问题。 -->
    <!-- https://github.com/element-plus/element-plus/issues/10172#issuecomment-1295794523 -->
    <el-dialog v-model="dialogVisible" style="min-width: 24rem;" :title="t(`local.title.${activeDialog}`)">
        <LoginForm v-if="activeDialog === 'login'" @forget-password="activeDialog = 'retrieve'" @login="login" />
        <RegisterForm v-else-if="activeDialog === 'register'" @login="login" />
        <RetrieveForm v-else @login="login" />
    </el-dialog>
</template>

<script lang="ts" setup>
// 注册、登录、找回密码的弹框及右上方按钮
import '@/styles/text.css';

import { ElButton, ElDialog, ElMessage } from 'element-plus';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import LoginForm from './LoginForm.vue';
import RegisterForm from './RegisterForm.vue';
import RetrieveForm from './RetrieveForm.vue';

import { httpErrorNotification } from '@/components/Notifications';
import { local, store } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const { proxy } = useCurrentInstance();

const dialogVisible = ref(false);
const activeDialog = ref<'login' | 'register' | 'retrieve'>('login');

onMounted(async () => {
    await proxy.$axios.get('api/userprofile/info/0').then(function (response) {
        store.login(response.data);
    }).catch((err) => {
        store.logout();
        if (err.status == 401) {
            console.log('401 is normal, indicating that the user is not logged in.');
            return;
        }
        httpErrorNotification(err);
    });
});

const login = (user: any) => {
    store.login(user);
    dialogVisible.value = false;
};

const logout = async () => {
    proxy.$axios.post('/userprofile/logout/',
        {},
    ).then(function (_response) {
        store.logout();
        ElMessage.success({ message: t('common.msg.logoutSuccess'), offset: 68 });
        dialogVisible.value = false;
    }).catch(httpErrorNotification);
};

const i18nMessages = {
    'zh-cn': { local: {
        menu: {
            login: '登录',
            logout: '退出',
            register: '注册',
        },
        title: {
            login: '用户登录',
            register: '用户注册',
            retrieve: '修改密码',
        },
    } },
    'en': { local: {
        menu: {
            login: 'Login',
            logout: 'Logout',
            register: 'Register',
        },
        title: {
            login: 'Login',
            register: 'Register',
            retrieve: 'Reset Password',
        },
    } },
    'de': { local: {
        menu: {
            login: 'Login',
            logout: 'Abmeldem',
            register: 'Registrieren',
        },
    } },
    'fr': { local: {
        menu: {
            login: 'Connexion',
        },
        title: {
            register: 'Créer un compte',
        },
    } },
    'pl': { local: {
        menu: {
            login: 'login',
            logout: 'wyloguj',
            register: 'zarejestruj się',
        },
        title: {
            login: 'login',
            retrieve: 'resetuj Hasło',
        },
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>


<style lang="less" scoped>
.fakemenuitem {
    height: v-bind("`${local.menu_height}px`");
    font-size: v-bind("`${local.menu_font_size}px`"); // Somehow doesn't work
}
</style>
