<template>
    <el-dialog v-model="visible" :title="$t('login.registerTitle')" width="400px" align-center draggable
        :lock-scroll="false" @close='resetForm(ruleFormRef)'>
        <el-form :model="registerForm" ref="ruleFormRef" status-icon>
            <!-- 用户名 -->
            <el-form-item prop="username" :label="$t('form.username')" ref="usernameFormRef">
                <el-input v-model="registerForm.username" prefix-icon="User" maxlength="20" show-word-limit
                    @input="usernameInputHandler" @change="usernameChangeHandler"></el-input>
            </el-form-item>
            <!-- 邮箱 -->
            <email-form-item v-model="registerForm.email" ref="emailFormRef" check-collision="true" />
            <!-- 邮箱验证码 -->
            <email-code-block v-model="registerForm.emailCode" :email="registerForm.email" type="register"
                :email-state="email_state" ref="emailCodeFormRef" />
            <!-- 密码 -->
            <password-confirm-block v-model="registerForm.password" ref="passwordFormRef" />
            <!-- 同意协议 -->
            <el-form-item prop="agreeTAC">
                <el-checkbox v-if="true" v-model="agree_TAC" name="checkoutSecret">{{
                    $t('login.agreeTAC1')
                    }}
                    <a target="_blank" :href="AXIOS_BASE_URL + '/agreement.html'">{{ $t('login.agreeTAC2')
                        }}</a>
                </el-checkbox>
            </el-form-item>
            <!-- 确认 -->
            <el-form-item>
                <el-button type="primary" @click="submitForm(ruleFormRef)" :disabled="confirm_disabled">{{
                    $t('login.registerConfirm') }}</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>

<script setup lang="ts">
import { FormInstance, ElFormItem, ElNotification } from 'element-plus';
import { computed, reactive, ref } from 'vue';
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import { containsControl } from '@/utils/strings';
// @ts-ignore
import outOfCharacter from 'out-of-character';
import { validateError, validateSuccess } from '@/utils/common/elFormValidate';
import { useI18n } from 'vue-i18n';
import emailFormItem from '../formItems/emailFormItem.vue';
import emailCodeBlock from '../formItems/emailCodeBlock.vue';
import passwordConfirmBlock from '../formItems/passwordConfirmBlock.vue';
import { local } from '@/store';

const visible = defineModel();
const emit = defineEmits(['login']);

const { proxy } = useCurrentInstance();
const t = useI18n();
const agree_TAC = ref(false);
const AXIOS_BASE_URL = import.meta.env.VITE_BASE_API;

// Element Plus 2.8.0
// el-form 有 rule 属性实现更方便的校验，但是功能受限，
// 主要体现在多个校验器的优先级混乱，所以只能直接改 el-form-item 的内部变量
// el-form-item 有直接的 error 属性，可以实现完美的本地化
// 但是现版本控制不了 state，为了代码简洁，暂时不用 error 的解决方案
const usernameFormRef = ref<typeof ElFormItem>();
const emailFormRef = ref<typeof emailFormItem>();
const emailCodeFormRef = ref<typeof emailCodeBlock>();
const passwordFormRef = ref<typeof passwordConfirmBlock>();

interface RegisterForm {
    username: string,
    password: string,
    email: string,
    emailCode: string,
}

const registerForm = reactive<RegisterForm>({
    username: "",
    password: "",
    email: "",
    emailCode: "",
})

const ruleFormRef = ref<FormInstance>()

const email_state = computed(() => {
    if (emailFormRef.value === undefined) return '';
    else return emailFormRef.value.validateState;
})
const confirm_disabled = computed(() => {
    return !(agree_TAC.value && usernameFormRef.value!.validateState === 'success' && emailFormRef.value!.validateState === 'success' && emailCodeFormRef.value!.validateState === 'success' && passwordFormRef.value!.validateState === 'success')
})

const usernameInputHandler = (value: string) => {
    if (value.length == 0) validateError(usernameFormRef, t.t('msg.usernameRequired'));
    else if (containsControl.test(value)) validateError(usernameFormRef, t.t('msg.illegalCharacter'));
    else usernameFormRef.value!.clearValidate();
}

const usernameChangeHandler = (value: string) => {
    if (value.length == 0) validateError(usernameFormRef, t.t('msg.usernameRequired'));
    else if (containsControl.test(value)) validateError(usernameFormRef, t.t('msg.illegalCharacter'));
    else if (outOfCharacter.replace(value).length == 0) validateError(usernameFormRef, t.t('msg.usernameInvalid'));
    else {
        proxy.$axios.get('userprofile/checkcollision/', { params: { username: value } }).then(function (response) {
            if (response.data === 'False') validateSuccess(usernameFormRef)
            else validateError(usernameFormRef, t.t('msg.usernameCollision'));
        }).catch(function (error) {
            if (error.code === "ERR_NETWORK") validateError(usernameFormRef, t.t('msg.connectionFail'));
            else validateError(usernameFormRef, t.t('msg.unknownError') + error);
        })
    }
}

const submitForm = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    if (confirm_disabled.value) return
    await proxy.$axios.post('userprofile/register/', {
        username: registerForm.username,
        password: registerForm.password,
        email: registerForm.email,
        email_key: emailCodeFormRef.value!.hashkey,
        email_captcha: registerForm.emailCode,
    }).then(function (response) {
        let data = response.data;
        if (data.type === 'success') {
            emit('login', data.user)
            ElNotification({
                title: t.t('msg.registerSuccess'),
                type: 'success',
                duration: local.notification_duration,
            })
        } else if (data.type === 'error') {
            if (data.object === 'emailcode') {
                emailCodeFormRef.value!.errorCode()
            }
        }
    })
}

const resetForm = (formEl: FormInstance | undefined) => {
    if (!formEl) return
    formEl.resetFields()
}

</script>