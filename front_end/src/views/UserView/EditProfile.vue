<template>
    <!-- 真实姓名 -->
    <div class="input-label">
        <div class="text text-large">
            {{ t('local.realname') }}
        </div>
        <div class="text text-small">
            {{ t('local.realnameTooltip') }}
        </div>
    </div>

    <!-- 母语名 -->
    <div class="input-label text">
        <div class="text">
            {{ t('local.localname') }}
        </div>
        <div class="text text-small">
            {{ t('local.localnameTooltip') }}
        </div>
    </div>
    <div>
        <div v-if="formStatus.realname.status === 'error'" class="text text-danger text-small">
            {{ formStatus.realname.errorMsg }}
        </div>
        <div v-else-if="formStatus.realname.status === 'success'" class="text text-small text-success">
            {{ t('local.updateSuccess') }}
        </div>
        <ElInput
            v-model="formStatus.realname.new" minlength="2"
            maxlength="100" show-word-limit :disabled="user.realname !== ''"
        />
    </div>

    <!-- 英文姓名 -->
    <div class="input-label">
        <div class="text">
            {{ t('local.englishName') }}
        </div>
        <div class="text text-small">
            {{ t('local.englishNameTooltip') }}
        </div>
    </div>
    <div>
        <div v-if="formStatus.firstname.status === 'error'" class="text text-danger text-small">
            {{ formStatus.firstname.errorMsg }}
        </div>
        <div v-else-if="formStatus.firstname.status === 'success'" class="text text-small text-success">
            {{ t('local.updateSuccess') }}
        </div>
        <ElInput v-model="formStatus.firstname.new" :placeholder="t('local.firstname')" minlength="1" maxlength="255" show-word-limit :disabled="user.firstname !== ''" />
        <div v-if="formStatus.lastname.status === 'error'" class="text text-danger text-small">
            {{ formStatus.lastname.errorMsg }}
        </div>
        <div v-else-if="formStatus.lastname.status === 'success'" class="text text-small text-success">
            {{ t('local.updateSuccess') }}
        </div>
        <ElInput v-model="formStatus.lastname.new" :placeholder="t('local.lastname')" minlength="1" maxlength="255" show-word-limit :disabled="user.lastname !== ''" />
    </div>

    <!-- 个性签名 -->
    <div class="input-label">
        <div class="text text-large">
            {{ t('local.signature') }}
        </div>
        <div class="text text-small">
            {{ t('local.signatureTooltip', { left: user.newSignatureBudget(new Date(Date.now())), next: toISODateTimeString(user.nextSignatureAvailable) }) }}
        </div>
        <div v-if="expTimeMs >= 200000" class="text text-small text-warning">
            {{ t('local.tooltipExpTime') }}
        </div>
    </div>
    <div>
        <div v-if="formStatus.signature.status === 'error'" class="text text-danger text-small">
            {{ formStatus.signature.errorMsg }}
        </div>
        <div v-else-if="formStatus.signature.status === 'success'" class="text text-small text-success">
            {{ t('local.updateSuccess') }}
        </div>
        <ElInput
            v-model="formStatus.signature.new" minlength="0"
            maxlength="4095" type="textarea" :rows="8" show-word-limit
            :disabled="signatureDisabled"
        />
    </div>

    <div style="margin-top: 1em">
        <ElButton type="primary" @click="updateProfile">
            {{ t('common.button.save') }}
        </ElButton>
        <ElButton type="info" @click="isEditing = false">
            {{ t('common.button.cancel') }}
        </ElButton>
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ElButton, ElInput } from 'element-plus';
import { computed, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { httpErrorNotification } from '@/components/Notifications';
import type { EnumMap } from '@/utils';
import { createEnumMap } from '@/utils';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { globalNow, toISODateTimeString } from '@/utils/datetime';
import { UserProfile } from '@/utils/userprofile';

const props = defineProps({
    expTimeMs: { type: Number, default: 999999 },
});

const { proxy } = useCurrentInstance();

const UpdateProfileFields = ['realname', 'firstname', 'lastname', 'signature'] as const;
type UpdateProfileField = typeof UpdateProfileFields[number];
interface formStatusSingle {
    new: string;
    status: '' | 'success' | 'error';
    errorMsg: string;
}

const user = defineModel('user', { type: UserProfile, default: () => new UserProfile() });
const isEditing = defineModel('isEditing', { type: Boolean, default: false });

const updating = ref(false);

const defaultFormStatus: formStatusSingle = {
    new: '',
    status: '',
    errorMsg: '',
};

const formStatus = ref<EnumMap<UpdateProfileField, formStatusSingle>>(
    createEnumMap(UpdateProfileFields, defaultFormStatus),
);

function refresh() {
    for (const field of UpdateProfileFields) {
        formStatus.value[field].new = user.value[field];
    }
}

watch(() => isEditing.value, () => {
    if (isEditing.value) refresh();
}, { immediate: true });

onMounted(refresh);

const signatureDisabled = computed(() => user.value.nextSignatureAvailable > globalNow.value || props.expTimeMs >= 200000);

type UpdateProfileResponseSingle = null
    | { type: 'success' }
    | { type: 'error'; object: string; category: string };

function processUpdateResponse(field: UpdateProfileField, data: UpdateProfileResponseSingle) {
    if (data === null) {
        formStatus.value[field].status = '';
        formStatus.value[field].errorMsg = '';
    } else if (data.type === 'success') {
        formStatus.value[field].status = 'success';
        formStatus.value[field].errorMsg = '';
        user.value[field] = formStatus.value[field].new;
        if (field === 'signature') {
            user.value.left_signature_n -= 1;
            user.value.last_change_signature = new Date(Date.now());
        }
    } else {
        formStatus.value[field].status = 'error';
        formStatus.value[field].errorMsg = t(`local.error.${data.object}.${data.category}`);
    }
}

async function updateProfile() {
    updating.value = true;
    const params = new FormData();
    for (const field of UpdateProfileFields) {
        if (formStatus.value[field].new !== user.value[field]) {
            params.append(field, formStatus.value[field].new);
        }
    }

    if (params.keys().next().done !== true) {
        await proxy.$axios.post(
            '/api/userprofile/update_profile',
            params,
        ).then((response) => {
            const data = response.data as EnumMap<UpdateProfileField, UpdateProfileResponseSingle>;
            for (const field of UpdateProfileFields) {
                processUpdateResponse(field, data[field]);
            }
        }).catch(httpErrorNotification);
    }
    updating.value = false;
    isEditing.value = false;
}

const i18nMessages = {
    'zh-cn': { local: {
        englishName: '英文姓名',
        englishNameTooltip: '用英文依次填写您的名和姓，让全世界的雷友认识您。',
        firstname: '名',
        lastname: '姓',
        localname: '本名',
        localnameTooltip: '使用您的本地语言填写完整姓名。这是上传录像所必需的信息。',
        realname: '真实姓名',
        realnameTooltip: '真实姓名一旦设置无法修改，请谨慎填写。如果有正当理由修改姓名，请联系管理员。',
        signature: '个性签名',
        tooltipExpTime: '高级sub200后才可以修改个性签名',
        updateSuccess: '修改成功',
        signatureTooltip: ({ named }: { named: { (key: 'left'): number; (key: 'next'): string } }) => {
            if (named('left') > 0) {
                return `您每月可获得一次签名修改次数。当前剩余${named('left')}次。`;
            } else {
                return `您每月可获得一次签名修改次数。当前没有修改次数。下次可修改：${named('next')}`;
            }
        },
        error: {
            censorship: {
                unknown: '机器审核发生未知错误，请联系管理员',
                illegal: '未通过机器审核，请更换内容或联系管理员进行人工审核',
            },
        },
    } },
    en: { local: {
        englishName: 'International Name',
        englishNameTooltip: 'Fill in your given name and family name in English to let minesweepers around the world know you.',
        firstname: 'Given Name',
        lastname: 'Family Name',
        localname: 'Local Name',
        localnameTooltip: 'Fill in your full name in your local language. This field is required to upload videos.',
        realname: 'Real Name',
        realnameTooltip: 'Your real name cannot be changed once set. If you have a legitimate reason to change your name, please contact a moderator.',
        signature: 'Signature',
        tooltipExpTime: 'Achieve expert sub200 to change signature',
        updateSuccess: 'Update successful',
        signatureTooltip: ({ named }: { named: { (key: 'left'): number; (key: 'next'): string } }) => {
            if (named('left') > 0) {
                return `You gain one chance to modify your signature each month. You have ${named('left')} chances remaining.`;
            } else {
                return `You gain one chance to modify your signature each month. You have no chance remaining. Next available on: ${named('next')}`;
            }
        },
        error: {
            censorship: {
                unknown: 'Unknown error occurred in censorship. Please contact a moderator',
                illegal: 'The content is blocked by censorship. Please change the text or contact a moderator for manual review',
            },
        },
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>

<style lang="less" scoped>
.input-label {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}
</style>
