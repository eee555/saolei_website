<!-- 
邮箱验证码表单项
发送验证码的前置条件：填写了有效邮箱，且通过了图形验证
-->
<template>
    <!-- 图形验证码 -->
    <el-form-item ref="captchaFormRef" :disabled="!email_success" :label="t('form.imageCaptcha')">
        <div style="display: flex">
            <el-input v-model.trim="captcha" prefix-icon="Key" class="code" maxlength="4"
                @input="captchaHandler"></el-input>
            &nbsp;
            <ValidCode ref="refValidCode" />
        </div>
    </el-form-item>
    <!-- 邮箱验证码 -->
    <el-form-item ref="emailCodeFormRef" prop="emailCode" :label="t('form.emailCode')">
        <div style="display: flex">
            <el-input v-model.trim="emailCode" prefix-icon="Key" maxlength="6" :disabled="captcha.length!=4" :placeholder="t(email_code_placeholder)"
                @input="emailCodeHandler"></el-input>
            &nbsp;
            <el-button :disabled="captcha.length!=4" @click="getEmailCaptcha(type)">
                <vue-countdown v-if="counting" v-slot="{ totalSeconds }" :time="60000" @end="counting = false;">
                    ({{ totalSeconds }})
                </vue-countdown>
                <span v-else>{{ t('common.button.send') }}</span>
            </el-button>
        </div>
    </el-form-item>
</template>

<script setup lang="ts">
import { validateError, validateSuccess } from '@/utils/common/elFormValidate';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { ElFormItem, ElNotification, ElButton, ElInput } from 'element-plus';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import ValidCode from '../ValidCode.vue';
import { local } from '@/store';
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
const emailCode = defineModel({ type: String, required: true });

const { proxy } = useCurrentInstance();
const { t } = useI18n();

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
    validateError(emailCodeFormRef, t('msg.emailCodeInvalid'))
}

defineExpose({ validateState, hashkey, errorCode })

const email_code_placeholder = computed(() => {
    if (prop.emailState !== 'success') return t('msg.emailRequired');
    else if (captchaFormRef.value?.validateState !== 'success') return t('msg.captchaRequired');
    else if (email_handling.value) return t('msg.pleaseWait');
    else if (email_success.value) return t('msg.pleaseSeeEmail');
    else return '';
})
const send_email_code_button_disabled = computed(() => {
    if (prop.emailState !== 'success') return true;
    else if (captchaFormRef.value?.validateState !== 'success') return true;
    else if (email_handling.value) return true;
    else return false;
})

const captchaHandler = (value: string) => {
    if (value.length == 0) validateError(captchaFormRef, t('msg.captchaRequired'));
    else validateSuccess(captchaFormRef);
}

const emailCodeHandler = (value: string) => {
    if (value.length == 0) validateError(emailCodeFormRef, t('msg.emailCodeRequired'));
    else validateSuccess(emailCodeFormRef);
}

const getEmailCaptcha = (type: string) => {
    if (prop.emailState !== 'success') return;
    if (email_success.value) {
        refreshCaptcha();
        validateError(captchaFormRef, t('msg.captchaRefresh'));
        email_success.value = false;
        return;
    }
    email_handling.value = true;
    counting.value = true;
    proxy.$axios.post('/userprofile/get_email_captcha/', {
        captcha: captcha.value,
        hashkey: refValidCode.value!.hashkey,
        email: prop.email,
        type: type,
    }).then(function (response) {
        const data = response.data;
        if (data.type == 'success') {
            captchaFormRef.value!.validateState = 'success';
            hashkey.value = data.hashkey;
            email_success.value = true;
            ElNotification({
                title: t('msg.emailSendSuccessTitle'),
                message: t('msg.emailSendSuccessMsg'),
                type: 'warning',
                duration: local.value.notification_duration,
            })
        } else if (data.type == 'error') {
            refreshCaptcha();
            if (data.object == 'captcha') {
                validateError(captchaFormRef, t('msg.captchaFail'));
                counting.value = false;
            } else if (data.object == 'email') {
                validateError(captchaFormRef, t('msg.captchaRefresh'));
                ElNotification({
                    title: t('msg.emailSendFailTitle'),
                    message: t('msg.emailSendFailMsg'),
                    type: 'error',
                    duration: local.value.notification_duration,
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