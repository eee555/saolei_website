<template>
    <!-- 密码 -->
    <el-form-item ref="passwordFormRef" :label="t('form.password')">
        <el-input 
            v-model="password" show-password prefix-icon="Lock" minlength="6" maxlength="20" show-word-limit
            @change="passwordHandler"
        />
    </el-form-item>
    <!-- 确认密码 -->
    <el-form-item ref="confirmPasswordFormRef" prop="password" :label="t('form.confirmPassword')">
        <el-input 
            v-model="confirmPassword" show-password prefix-icon="Lock" minlength="6" maxlength="20"
            @change="confirmPasswordHandler"
        />
    </el-form-item>
</template>

<script setup lang="ts">
import { validateError, validateSuccess } from '@/utils/common/elFormValidate';
import { ElFormItem, ElInput } from 'element-plus';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';

const password = defineModel({ type: String, required: true });

const { t } = useI18n();

const confirmPassword = ref('');

const passwordFormRef = ref<typeof ElFormItem>();
const confirmPasswordFormRef = ref<typeof ElFormItem>();

const validateState = computed(() => { return confirmPasswordFormRef.value!.validateState });
defineExpose({ validateState })

const passwordHandler = (value: string) => {
    if (value.length == 0) validateError(passwordFormRef, t('msg.passwordRequired'))
    if (value.length < 6) validateError(passwordFormRef, t('msg.passwordMinimum'));
    else validateSuccess(passwordFormRef);
    if (confirmPasswordFormRef.value!.validateState !== '') {
        if (value !== confirmPassword.value) validateError(confirmPasswordFormRef, t('msg.confirmPasswordMismatch'));
        else validateSuccess(confirmPasswordFormRef);
    }
}

const confirmPasswordHandler = (value: any) => {
    if (value !== password.value) validateError(confirmPasswordFormRef, t('msg.confirmPasswordMismatch'));
    else validateSuccess(confirmPasswordFormRef);
}

</script>