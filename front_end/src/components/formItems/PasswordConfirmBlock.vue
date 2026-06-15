<template>
    <!-- 密码 -->
    <ElFormItem ref="passwordFormRef" :label="t('form.password')">
        <ElInput
            v-model="password" show-password prefix-icon="Lock" minlength="6" maxlength="20" show-word-limit
            @change="passwordHandler"
        />
    </ElFormItem>
    <!-- 确认密码 -->
    <ElFormItem ref="confirmPasswordFormRef" prop="password" :label="t('form.confirmPassword')">
        <ElInput
            v-model="confirmPassword" show-password prefix-icon="Lock" minlength="6" maxlength="20"
            @change="confirmPasswordHandler"
        />
    </ElFormItem>
</template>

<script setup lang="ts">
import { ElFormItem, ElInput } from 'element-plus';
import { computed, ref, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';

import { validateError, validateSuccess } from '@/utils/common/elFormValidate';

const password = defineModel({ type: String, required: true });

const { t } = useI18n();

const confirmPassword = ref('');

const passwordFormRef = useTemplateRef('passwordFormRef');
const confirmPasswordFormRef = useTemplateRef('confirmPasswordFormRef');

const validateState = computed(() => { return confirmPasswordFormRef.value!.validateState; });
defineExpose({ validateState });

const passwordHandler = (value: string) => {
    if (value.length == 0) validateError(passwordFormRef, t('msg.passwordRequired'));
    else if (value.length < 6) validateError(passwordFormRef, t('msg.passwordMinimum'));
    else validateSuccess(passwordFormRef);
    if (confirmPasswordFormRef.value!.validateState !== '') {
        if (value !== confirmPassword.value) validateError(confirmPasswordFormRef, t('msg.confirmPasswordMismatch'));
        else validateSuccess(confirmPasswordFormRef);
    }
};

const confirmPasswordHandler = (value: any) => {
    if (value !== password.value) validateError(confirmPasswordFormRef, t('msg.confirmPasswordMismatch'));
    else validateSuccess(confirmPasswordFormRef);
};
</script>
