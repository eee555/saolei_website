<template>
    <el-dialog v-model="visible" :title="$t('forgetPassword.title')" width="400px" align-center draggable
    :lock-scroll="false" @close='resetForm(ruleFormRef)'>
        <el-form>
            <!-- 邮箱 -->
            <email-form-item v-model="retrieveForm.email" ref="emailFormRef" check-collision="false"></email-form-item>
            <!-- 邮箱验证码 -->
            <email-code-block v-model="retrieveForm.emailCode" :email="retrieveForm.email" type="register" :email-state="email_state" ref="emailCodeFormRef"/>
            <!-- 密码 -->
            <password-confirm-block v-model="retrieveForm.password" ref="passwordFormRef" />
            <!-- 确认 -->
            <el-form-item>
                <el-button type="primary" @click="submitForm(ruleFormRef)" :disabled="confirm_disabled">{{
                    $t('register.confirm') }}</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>

<script setup lang="ts">
import { ElFormItem, FormInstance } from 'element-plus';
import { computed, reactive, ref } from 'vue';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import emailFormItem from '../formItems/emailFormItem.vue';
import emailCodeBlock from '../formItems/emailCodeBlock.vue';
import passwordConfirmBlock from '../formItems/passwordConfirmBlock.vue';

const visible = defineModel();
const emit = defineEmits(['login']);

const { proxy } = useCurrentInstance();

const emailFormRef = ref<typeof ElFormItem>();
const emailCodeFormRef = ref<typeof emailCodeBlock>();
const passwordFormRef = ref<typeof passwordConfirmBlock>();

interface RetrieveForm {
    email: string,
    emailCode: string,
    password: string,
}

const retrieveForm = reactive<RetrieveForm>({
    email: "",
    emailCode: "",
    password: "",
})

const ruleFormRef = ref<FormInstance>()

const email_state = computed(() => {
    if (emailFormRef.value === undefined) return '';
    else return emailFormRef.value.validateState;
})
const confirm_disabled = computed(() => {
    return !(emailFormRef.value!.validateState === 'success' && emailCodeFormRef.value!.validateState === 'success' && passwordFormRef.value!.validateState === 'success')
})

const submitForm = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    if (confirm_disabled) return
    await proxy.$axios.post('userprofile/retrieve/', {
        password: retrieveForm.password,
        email: retrieveForm.email,
        email_key: emailCodeFormRef.value!.hashkey,
        email_captcha: retrieveForm.emailCode,
    }).then(function (response) {
        let data = response.data;
        if (data.type == 'success') {
            emit('login', data.user)
        }
    })
}

const resetForm = (formEl: FormInstance | undefined) => {
    if (!formEl) return
    formEl.resetFields()
}

</script>