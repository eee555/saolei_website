<template>
    <el-form-item ref="emailFormRef" prop="email" :label="t('form.email')">
        <el-input 
            v-model="email" prefix-icon="Message" type="email" @input="emailInputHandler"
            @change="emailChangeHandler"
        />
    </el-form-item>
</template>

<script setup lang="ts">
import { validateError, validateSuccess } from '@/utils/common/elFormValidate';
import { ElFormItem, ElInput } from 'element-plus';
import { computed, ref } from 'vue';
// @ts-ignore
import isEmail from 'validator/lib/isEmail.js';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { useI18n } from 'vue-i18n';

const email = defineModel({ type: String, required: true });
const prop = defineProps({
    checkCollision: {
        type: String,
        default: '',
    },
})

const { proxy } = useCurrentInstance();
const { t } = useI18n();

const emailFormRef = ref<typeof ElFormItem>();
const validateState = computed(() => { return emailFormRef.value!.validateState });

defineExpose({ validateState })

const emailInputHandler = (value: string) => {
    if (value.length == 0) validateError(emailFormRef, t('msg.emailRequired'));
    else emailFormRef.value!.clearValidate();
}

const emailChangeHandler = (value: string) => {
    if (value.length == 0) validateError(emailFormRef, t('msg.emailRequired'));
    else if (!isEmail(value)) validateError(emailFormRef, t('msg.emailInvalid'));
    else if (prop.checkCollision !== '') {
        proxy.$axios.get('userprofile/checkcollision/', { params: { email: value } }).then(function (response) {
            if (response.data === 'True' && prop.checkCollision === 'true') validateError(emailFormRef, t('msg.emailCollision'));
            else if (response.data === 'False' && prop.checkCollision === 'false') validateError(emailFormRef, t('msg.emailNoCollision'));
            else validateSuccess(emailFormRef);
        }).catch(function (error) {
            if (error.code === "ERR_NETWORK") validateError(emailFormRef, t('msg.connectionFail'));
            else validateError(emailFormRef, t('msg.unknownError') + error);
        })
    }
}

</script>