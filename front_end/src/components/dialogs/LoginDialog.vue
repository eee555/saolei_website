<template>
    <el-dialog 
        v-model="visible" :title="t('login.loginTitle')" width="400px" align-center draggable
        :lock-scroll="false" @close="resetForm(ruleFormRef); emit('close')"
    >
        <el-form ref="ruleFormRef" :rules="rules" :model="loginForm">
            <!-- 用户名 -->
            <el-form-item prop="username" :label="t('form.username')">
                <el-input v-model="loginForm.username" prefix-icon="User" maxlength="20" show-word-limit />
            </el-form-item>
            <!-- 密码 -->
            <el-form-item prop="password" :label="t('form.password')" :error="passwordError">
                <el-input v-model="loginForm.password" maxlength="20" show-password prefix-icon="Lock" />
            </el-form-item>
            <!-- 验证码 -->
            <el-form-item prop="captcha" :label="t('form.captcha')" :error="captchaError">
                <div style="display: flex;">
                    <el-input v-model.trim="loginForm.captcha" prefix-icon="Key" class="code" maxlength="4" />
                    &nbsp;
                    <ValidCode ref="refValidCode" />
                </div>
            </el-form-item>
            <!-- 记住我 -->
            <el-form-item>
                <el-checkbox v-model="remember_me" :label="t('login.keepMeLoggedIn')" class="rememberMe" />
            </el-form-item>
            <!-- 忘记密码 -->
            <el-form-item>
                <el-link 
                    :underline="false" type="primary"
                    style="vertical-align: bottom;" @click="emit('forgetPassword')"
                >
                    {{ t('login.forgetPassword') }}
                </el-link>
            </el-form-item>
            <!-- 确认 -->
            <el-form-item>
                <el-button type="primary" @click="submitForm(ruleFormRef)">
                    {{ t('login.loginConfirm') }}
                </el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>

<script setup lang="ts">
import { FormRules, FormInstance, ElDialog, ElForm, ElInput, ElFormItem, ElCheckbox, ElLink, ElButton} from 'element-plus';
import { reactive, ref } from 'vue';
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import ValidCode from "@/components/ValidCode.vue";
import { useI18n } from 'vue-i18n';
import { httpErrorNotification } from "@/components/Notifications";

const visible = defineModel({ type: Boolean, default: false });
const emit = defineEmits(['close', 'forgetPassword', 'login']);

const { t } = useI18n();
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
        { required: true, message: t('msg.usernameRequired') },
    ],
    password: [
        { required: true, message: t('msg.passwordRequired') },
    ],
    captcha: [
        { required: true, message: t('msg.captchaRequired') },
    ],
})

const submitForm = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    await formEl.validate((valid, _fields) => {
        if (!valid) return;
        const user_id = localStorage.getItem("history_user_id");
        proxy.$axios.post('userprofile/login/', {
            user_id: user_id, // 为空时post会自动忽略该项
            username: loginForm.username,
            password: loginForm.password,
            captcha: loginForm.captcha,
            hashkey: refValidCode.value?.hashkey,
        }).then(function (response) {
            const data = response.data;
            if (data.type == 'success') {
                emit('login', data.user, remember_me.value)
            } else if (data.type == 'error') {
                if (data.category == 'captcha') {
                    captchaError.value = t('msg.captchaFail');
                    if (refValidCode.value !== undefined) refValidCode.value.refreshPic();
                } else if (data.category == 'password') {
                    passwordError.value = t('msg.usernamePasswordInvalid');
                }
            }
        }).catch(httpErrorNotification)
    })
}

const resetForm = (formEl: FormInstance | undefined) => {
    if (!formEl) return
    formEl.resetFields()
}

</script>