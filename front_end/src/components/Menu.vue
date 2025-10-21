<!-- 已弃用 -->
<template>
    <div style="float: right;">
        <div style="display: inline-flex;">
            <Login @login="user_login" @logout="user_logout" />
        </div>
        <span style="width:12px; display:inline-block" />|<span style="width:12px; display:inline-block" />
        <Downloads />
        <span style="width:12px; display:inline-block" />|<span style="width:12px; display:inline-block" />
        <FriendlyLink />
        <span style="width:12px; display:inline-block" />|<span style="width:12px; display:inline-block" />
        <Thanks />
    </div>
</template>

<script lang="ts" setup>
// 注册、登录的弹框及右上方按钮
import { onMounted, ref } from 'vue';

import Login from './Login.vue';

import Downloads from '@/components/dialogs/Downloads.vue';
import FriendlyLink from '@/components/dialogs/FriendlyLinks.vue';
import Thanks from '@/components/dialogs/Thanks.vue';
import { LoginStatus } from '@/utils/common/structInterface';
// import { AXIOS_BASE_URL } from '../config';

const login_status = ref(LoginStatus.NotLogin);


const emit = defineEmits(['login', 'logout']);

onMounted(() => {


});


const user_login = () => {
    // 配合孙组件向爷组件传
    emit('login');
};

const user_logout = () => {
    // 配合孙组件向爷组件传
    emit('logout');
};



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









