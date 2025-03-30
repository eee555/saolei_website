<template>
    <el-dialog
        v-model="visible" :title="t('login.retrieveTitle')" width="400px" align-center draggable
        :lock-scroll="false" @close="resetForm(ruleFormRef)"
    >
        <el-form ref="ruleFormRef" :model="retrieveForm" status-icon>
            <!-- 邮箱 -->
            <email-form-item ref="emailFormRef" v-model="retrieveForm.email" check-collision="false" />
            <!-- 邮箱验证码 -->
            <email-code-block
                ref="emailCodeFormRef" v-model="retrieveForm.emailCode" :email="retrieveForm.email" type="register"
                :email-state="email_state"
            />
            <!-- 密码 -->
            <password-confirm-block ref="passwordFormRef" v-model="retrieveForm.password" />
            <!-- 确认 -->
            <el-form-item>
                <el-button type="primary" :disabled="confirm_disabled" @click="submitForm(ruleFormRef)">
                    {{
                        t('login.retrieveConfirm') }}
                </el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>

<script setup lang="ts">
import { ElFormItem, ElNotification, FormInstance, ElForm, ElButton, ElDialog } from 'element-plus';
import { computed, reactive, ref } from 'vue';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import emailFormItem from '../formItems/emailFormItem.vue';
import emailCodeBlock from '../formItems/emailCodeBlock.vue';
import passwordConfirmBlock from '../formItems/passwordConfirmBlock.vue';
import { local } from '@/store';
import { useI18n } from 'vue-i18n';

const visible = defineModel({ type: Boolean, default: false });
const emit = defineEmits(['login']);

const { proxy } = useCurrentInstance();
const { t } = useI18n();

const emailFormRef = ref<typeof ElFormItem>();
const emailCodeFormRef = ref<typeof emailCodeBlock>();
const passwordFormRef = ref<typeof passwordConfirmBlock>();

interface RetrieveForm {
    email: string;
    emailCode: string;
    password: string;
}

const retrieveForm = reactive<RetrieveForm>({
    email: '',
    emailCode: '',
    password: '',
});

const ruleFormRef = ref<FormInstance>();

const email_state = computed(() => {
    if (emailFormRef.value === undefined) return '';
    else return emailFormRef.value.validateState;
});
const confirm_disabled = computed(() => {
    return !(emailFormRef.value !== undefined && emailFormRef.value!.validateState === 'success' && emailCodeFormRef.value!.validateState === 'success' && passwordFormRef.value!.validateState === 'success');
});

const submitForm = async (formEl: FormInstance | undefined) => {
    if (!formEl) return;
    if (confirm_disabled.value) return;
    await proxy.$axios.post('userprofile/retrieve/', {
        password: retrieveForm.password,
        email: retrieveForm.email,
        email_key: emailCodeFormRef.value!.hashkey,
        email_captcha: retrieveForm.emailCode,
    }).then(function (response) {
        const data = response.data;
        if (data.type == 'success') {
            emit('login', data.user);
            ElNotification({
                title: t('msg.passwordChanged'),
                type: 'success',
                duration: local.value.notification_duration,
            });
        } else if (data.type === 'error') {
            if (data.object === 'emailcode') {
                emailCodeFormRef.value!.errorCode();
            }
        }
    });
};

const resetForm = (formEl: FormInstance | undefined) => {
    if (!formEl) return;
    formEl.resetFields();
};

</script>
