<!-- 
邮箱验证码表单项
发送验证码的前置条件：填写了有效邮箱，且通过了图形验证
-->
<template>
    <!-- 图形验证码 -->
    <el-form-item :disabled="!email_success" :label="$t('register.captcha')" ref="captchaFormRef">
        <div style="display: flex">
            <el-input v-model.trim="captcha" prefix-icon="Key" class="code" maxlength="6"
                @input="captchaHandler"></el-input>
            &nbsp;
            <ValidCode ref="refValidCode" />
        </div>
    </el-form-item>
    <!-- 邮箱验证码 -->
    <el-form-item prop="emailCode" :label="$t('register.emailCode')" ref="emailCodeFormRef">
        <div style="display: flex">
        <el-input v-model.trim="emailCode" prefix-icon="Key" maxlength="6"
            :disabled="!email_success" @change="emailCodeHandler" :placeholder="send_email_code_button"></el-input>
        &nbsp;
        <el-button @click="getEmailCaptcha(type)" :disabled="send_email_code_button_disabled || counting">
            <vue-countdown v-if="counting" :time="60000" @end="counting = false;" v-slot="{ totalSeconds }">
                ({{ totalSeconds }})
            </vue-countdown>
            <span v-else>发送</span>
        </el-button>
        </div>
    </el-form-item>
</template>

<script setup lang="ts">
import { validateError, validateSuccess } from '@/utils/common/elFormValidate';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { ElFormItem, ElNotification } from 'element-plus';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import ValidCode from '../ValidCode.vue';
import { useLocalStore } from '@/store';
import VueCountdown from '@chenfengyuan/vue-countdown';

const prop = defineProps({
    type: { // 邮件模板，参考后端
        type: String,
        default: 'register',
    },
    email: {
        type: String,
        required: true,
    },
    emailState: {// 邮箱表单项的状态，参考el-form文档
        type: String,
        default: 'success',
    }
})
const emailCode = defineModel();

const { proxy } = useCurrentInstance();
const t = useI18n();
const local = useLocalStore();

const captcha = ref(''); // 图形验证码
const hashkey = ref(''); // 邮箱验证码hash
const email_success = ref(false); // 邮件发送成功
const email_handling = ref(false); // 正在校验图形验证码与发送邮件
const counting = ref(false);

const refValidCode = ref<typeof ValidCode>();
const captchaFormRef = ref<typeof ElFormItem>();
const emailCodeFormRef = ref<typeof ElFormItem>();

// 获取验证状态
const validateState = computed(() => { return emailCodeFormRef.value!.validateState });

// 由外部验证后，若不正确则传入修改验证状态
const errorCode = () => {
    validateError(emailCodeFormRef,'邮箱验证码过期或不正确')
}

defineExpose({ validateState, hashkey, errorCode })

const send_email_code_button = computed(() => {
    if (prop.emailState !== 'success') return '请输入邮箱';
    else if (captchaFormRef.value?.validateState !== 'success') return '请输入图形验证码';
    else if (email_handling.value) return '请稍候';
    else if (email_success.value) return '请查看邮箱';
    else return '发送邮箱验证码';
})
const send_email_code_button_disabled = computed(() => {
    if (prop.emailState !== 'success') return true;
    else if (captchaFormRef.value?.validateState !== 'success') return true;
    else if (email_handling.value) return true;
    else return false;
})

const captchaHandler = (value: string) => {
    if (value.length == 0) validateError(captchaFormRef, t.t('validator.captchaRequired'));
    else validateSuccess(captchaFormRef);
}

const emailCodeHandler = (value: string) => {
    if (value.length == 0) validateError(emailCodeFormRef, t.t('validator.emailCodeRequired'));
    else validateSuccess(emailCodeFormRef);
}

const getEmailCaptcha = (type: string) => {
    if (prop.emailState !== 'success') return;
    if (email_success.value) {
        refreshCaptcha();
        validateError(captchaFormRef, t.t('validator.captchaRefresh'));
        email_success.value=false;
        return;
    }
    email_handling.value = true;
    counting.value = true;
    proxy.$axios.post('/userprofile/get_email_captcha/', {
        captcha: captcha.value,
        hashkey: refValidCode.value!.hashkey,
        email: prop.email,
        type: prop.type,
    }).then(function (response) {
        let data = response.data;
        if (data.type == 'success') {
            captchaFormRef.value!.validateState = 'success';
            hashkey.value = data.hashkey;
            email_success.value = true;
            ElNotification({
                title: '邮件发送成功！',
                message: '请至邮箱查看',
                type: 'warning',
                duration: local.notification_duration,
            })
        } else if (data.type == 'error') {
            refreshCaptcha();
            if (data.object == 'captcha') {
                validateError(captchaFormRef, t.t('validator.captchaFail'));
            } else if (data.object == 'email') {
                validateError(captchaFormRef, t.t('validator.captchaRefresh'));
                ElNotification({
                    title: '邮件发送失败！',
                    message: '请重新输入图形验证码并尝试。如果该情况反复发生，请联系开发者。',
                    type: 'error',
                    duration: local.notification_duration,
                })
            }
        }
    });
    email_handling.value = false;
}

const refreshCaptcha = () => {
    refValidCode.value!.refreshPic();
    captcha.value = '';
}

</script>