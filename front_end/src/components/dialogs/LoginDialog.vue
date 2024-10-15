<template>
    <el-dialog v-model="visible" :title="$t('login.loginTitle')" width="400px" align-center draggable
        :lock-scroll="false" @close="resetForm(ruleFormRef); emit('close')">
        <el-form :rules="rules" :model="loginForm" ref="ruleFormRef">
            <!-- 用户名 -->
            <el-form-item prop="username" :label="$t('form.username')">
                <el-input v-model="loginForm.username" prefix-icon="User" maxlength="20" show-word-limit></el-input>
            </el-form-item>
            <!-- 密码 -->
            <el-form-item prop="password" :label="$t('form.password')" :error="passwordError">
                <el-input v-model="loginForm.password" maxlength="20" show-password prefix-icon="Lock"></el-input>
            </el-form-item>
            <!-- 验证码 -->
            <el-form-item prop="captcha" :label="$t('form.captcha')" :error="captchaError">
                <div style="display: flex;">
                    <el-input v-model.trim="loginForm.captcha" prefix-icon="Key" class="code" maxlength="4"></el-input>
                    &nbsp;
                    <ValidCode ref="refValidCode" />
                </div>
            </el-form-item>
            <!-- 记住我 -->
            <el-form-item>
                <el-checkbox :label="$t('login.keepMeLoggedIn')" class="rememberMe" v-model="remember_me"></el-checkbox>
            </el-form-item>
            <!-- 忘记密码 -->
            <el-form-item>
                <el-link @click="emit('forgetPassword')" :underline="false" type="primary"
                    style="vertical-align: bottom;">{{ $t('login.forgetPassword') }}</el-link>
            </el-form-item>
            <!-- 确认 -->
            <el-form-item>
                <el-button type="primary" @click="submitForm(ruleFormRef)">{{ $t('login.loginConfirm') }}</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>

<script setup lang="ts">
import { FormRules, FormInstance, ElNotification } from 'element-plus';
import { reactive, ref } from 'vue';
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import ValidCode from "@/components/ValidCode.vue";
import { useI18n } from 'vue-i18n';

const visible = defineModel();
const emit = defineEmits(['close', 'forgetPassword', 'login']);

const t = useI18n();
const { proxy } = useCurrentInstance();

const refValidCode = ref<typeof ValidCode>();
const remember_me = ref(false);
const captchaError = ref("");
const passwordError = ref("");

interface LoginForm {
    username: string,
    password: string,
    captcha: string,
}

const loginForm = reactive<LoginForm>({
    username: "",
    password: "",
    captcha: "",
})

const ruleFormRef = ref<FormInstance>()

const rules = reactive<FormRules<LoginForm>>({
    username: [
        { required: true, message: t.t('msg.usernameRequired') },
    ],
    password: [
        { required: true, message: t.t('msg.passwordRequired') },
    ],
    captcha: [
        { required: true, message: t.t('msg.captchaRequired') },
    ],
})

const submitForm = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    await formEl.validate((valid, fields) => {
        if (!valid) return;
        let _id = localStorage.getItem("history_user_id");
        proxy.$axios.post('userprofile/login/', {
            user_id: _id, // 为空时post会自动忽略该项
            username: loginForm.username,
            password: loginForm.password,
            captcha: loginForm.captcha,
            hashkey: refValidCode.value?.hashkey,
        }).then(function (response) {
            let data = response.data;
            if (data.type == 'success') {
                emit('login', data.user, remember_me.value)
            } else if (data.type == 'error') {
                if (data.category == 'captcha') {
                    captchaError.value = t.t('msg.captchaFail');
                    if (refValidCode.value !== undefined) refValidCode.value.refreshPic();
                } else if (data.category == 'password') {
                    passwordError.value = t.t('msg.usernamePasswordInvalid');
                }
            }
        }).catch(function (error) {
            
        })
    })
}

const resetForm = (formEl: FormInstance | undefined) => {
    if (!formEl) return
    formEl.resetFields()
}

</script>