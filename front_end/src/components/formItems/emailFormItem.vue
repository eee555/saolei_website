<template>
    <ElFormItem ref="emailFormRef" prop="email" :label="t('form.email')">
        <ElInput
            v-model="email" prefix-icon="Message" type="email" @input="emailInputHandler"
            @change="emailChangeHandler"
        />
    </ElFormItem>
</template>

<script setup lang="ts">
import { ElFormItem, ElInput } from 'element-plus';
import isEmail from 'validator/lib/isEmail';
import { computed, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';

import { validateError, validateSuccess } from '@/utils/common/elFormValidate';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const prop = defineProps({
    checkCollision: {
        type: String,
        default: '',
    },
});
const email = defineModel({ type: String, required: true });
const { proxy } = useCurrentInstance();
const { t } = useI18n();

const emailFormRef = useTemplateRef('emailFormRef');
const validateState = computed(() => { return emailFormRef.value!.validateState; });

defineExpose({ validateState });

const emailInputHandler = (value: string) => {
    if (value.length == 0) validateError(emailFormRef, t('msg.emailRequired'));
    else emailFormRef.value!.clearValidate();
};

const emailChangeHandler = (value: string) => {
    if (value.length == 0) validateError(emailFormRef, t('msg.emailRequired'));
    else if (!isEmail(value)) validateError(emailFormRef, t('msg.emailInvalid'));
    else if (prop.checkCollision !== '') {
        proxy.$axios.get('userprofile/checkcollision/', { params: { email: value } }).then(function (response) {
            if (response.data === 'True' && prop.checkCollision === 'true') validateError(emailFormRef, t('msg.emailCollision'));
            else if (response.data === 'False' && prop.checkCollision === 'false') validateError(emailFormRef, t('msg.emailNoCollision'));
            else validateSuccess(emailFormRef);
        }).catch(function (error) {
            if (error.code === 'ERR_NETWORK') validateError(emailFormRef, t('msg.connectionFail'));
            else validateError(emailFormRef, t('msg.unknownError') + error);
        });
    }
};
</script>
