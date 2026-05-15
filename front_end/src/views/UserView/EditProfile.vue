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
        <el-input
            v-model="newRealName" minlength="2"
            maxlength="100" show-word-limit
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
        <el-input v-model="newFirstName" :placeholder="t('local.firstname')" minlength="1" maxlength="255" show-word-limit />
        <el-input v-model="newLastName" :placeholder="t('local.lastname')" minlength="1" maxlength="255" show-word-limit />
    </div>

    <!-- 个性签名 -->
    <div class="input-label">
        {{ t('profile.signature') }}
    </div>
    <div>
        <el-input
            v-model="newSignature" :placeholder="t('profile.signatureInput')" minlength="0"
            maxlength="4095" type="textarea" :rows="8" show-word-limit
        />
    </div>

    <el-button type="primary" @click="updateProfile">
        {{ t('common.button.confirm') }}
    </el-button>
    <el-button type="info" @click="emit('close')">
        {{ t('common.button.cancel') }}
    </el-button>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ElButton, ElInput } from 'element-plus';
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { httpErrorNotification } from '@/components/Notifications';
import { store } from '@/store';
import { EnumMap } from '@/utils';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const { proxy } = useCurrentInstance();

const emit = defineEmits(['close']);

const props = defineProps({
    isEditing: { type: Boolean, default: false },
});

const newRealName = ref('');
const newFirstName = ref('');
const newLastName = ref('');
const newSignature = ref('');
const updating = ref(false);

const statusRealName = ref({
    status: '',
    errorMsg: '',
});
const statusFirstName = ref({
    status: '',
    errorMsg: '',
});
const statusLastName = ref({
    status: '',
    errorMsg: '',
});
const statusSignature = ref({
    status: '',
    errorMsg: '',
});

watch(() => props.isEditing, () => {
    if (props.isEditing) {
        newRealName.value = store.user.realname;
        newFirstName.value = store.user.firstname;
        newLastName.value = store.user.lastname;
        newSignature.value = store.user.signature;
    }
}, { immediate: true });


type UpdateProfileField = 'realname' | 'firstname' | 'lastname' | 'signature';
type UpdateProfileResponseSingle =
    | null
    | { type: 'success' }
    | { type: 'error'; object: string; category: string };

function processUpdateResponse(data: UpdateProfileResponseSingle) {
    if (data === null) return {
        status: '',
        errorMsg: '',
    };
    if (data.type === 'success') return {
        status: 'success',
        errorMsg: '',
    };
    if (data.type === 'error') return {
        status: 'error',
        errorMsg: t(`local.error.${data.object}.${data.category}`),
    };
    throw new Error('This branch should never be reached. Please report this bug.');
}

async function updateProfile() {
    updating.value = true;
    const params = new FormData();
    if (newRealName.value !== store.user.realname) {
        params.append('realname', newRealName.value);
    }
    if (newFirstName.value !== store.user.firstname) {
        params.append('firstname', newFirstName.value);
    }
    if (newLastName.value !== store.user.lastname) {
        params.append('lastname', newLastName.value);
    }
    if (newSignature.value !== store.user.signature) {
        params.append('signature', newSignature.value);
    }
    await proxy.$axios.post(
        '/api/userprofile/update_profile',
        params,
    ).then((response) => {
        const data = response.data as EnumMap<UpdateProfileField, UpdateProfileResponseSingle>;
        statusRealName.value = processUpdateResponse(data.realname);
        statusFirstName.value = processUpdateResponse(data.firstname);
        statusLastName.value = processUpdateResponse(data.lastname);
        statusSignature.value = processUpdateResponse(data.signature);
    }).catch(httpErrorNotification);
    updating.value = false;
    emit('close');
}

const i18nMessages = {
    'zh-cn': { local: {
        englishName: '英文姓名',
        englishNameTooltip: '用英文依次填写您的名和姓，让全世界的雷友认识您。',
        firstname: '名',
        lastname: '姓',
        localname: '本名',
        localnameTooltip: '使用您的本地语言填写完整姓名。',
        realname: '真实姓名',
        realnameTooltip: '真实姓名一旦设置无法修改，请谨慎填写。如果有正当理由修改姓名，请联系管理员。',
        signature: '个性签名',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>
