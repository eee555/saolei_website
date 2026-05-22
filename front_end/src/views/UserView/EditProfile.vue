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
            v-model="formStatus.realname.new" minlength="2"
            maxlength="100" show-word-limit :disabled="store.user.realname !== ''"
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
        <el-input v-model="formStatus.firstname.new" :placeholder="t('local.firstname')" minlength="1" maxlength="255" show-word-limit :disabled="store.user.firstname !== ''" />
        <el-input v-model="formStatus.lastname.new" :placeholder="t('local.lastname')" minlength="1" maxlength="255" show-word-limit :disabled="store.user.lastname !== ''" />
    </div>

    <!-- 个性签名 -->
    <div class="input-label text text-large">
        {{ t('local.signature') }}
    </div>
    <div>
        <el-input
            v-model="formStatus.signature.new" minlength="0"
            maxlength="4095" type="textarea" :rows="8" show-word-limit
        />
    </div>

    <div style="margin-top: 1em">
        <el-button type="primary" @click="updateProfile">
            {{ t('common.button.save') }}
        </el-button>
        <el-button type="info" @click="emit('close')">
            {{ t('common.button.cancel') }}
        </el-button>
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ElButton, ElInput } from 'element-plus';
import { onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { httpErrorNotification } from '@/components/Notifications';
import { store } from '@/store';
import { createEnumMap, EnumMap } from '@/utils';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const { proxy } = useCurrentInstance();

const emit = defineEmits(['close']);

const UpdateProfileFields = ['realname', 'firstname', 'lastname', 'signature'] as const;
type UpdateProfileField = typeof UpdateProfileFields[number];
interface formStatusSingle {
    new: string;
    status: '' | 'success' | 'error';
    errorMsg: string;
}

const props = defineProps({
    isEditing: { type: Boolean, default: false },
});

const updating = ref(false);

const formStatus = ref<EnumMap<UpdateProfileField, formStatusSingle>>(
    createEnumMap(
        UpdateProfileFields,
        {
            new: '',
            status: '' as '' | 'success' | 'error',
            errorMsg: '',
        },
    ),
);

function refresh() {
    for (const field of UpdateProfileFields) {
        formStatus.value[field].new = store.user[field];
    }
}

watch(() => props.isEditing, () => {
    if (props.isEditing) refresh();
}, { immediate: true });

onMounted(refresh);

type UpdateProfileResponseSingle =
    | null
    | { type: 'success' }
    | { type: 'error'; object: string; category: string };

function processUpdateResponse(field: UpdateProfileField, data: UpdateProfileResponseSingle) {
    if (data === null) {
        formStatus.value[field].status = '';
        formStatus.value[field].errorMsg = '';
    } else if (data.type === 'success') {
        formStatus.value[field].status = 'success';
        formStatus.value[field].errorMsg = '';
        store.user[field] = formStatus.value[field].new;
    } else if (data.type === 'error') {
        formStatus.value[field].status = 'error';
        formStatus.value[field].errorMsg = t(`local.error.${data.object}.${data.category}`);
    } else {
        throw new Error('This branch should never be reached. Please report this bug.');
    }
}

async function updateProfile() {
    updating.value = true;
    const params = new FormData();
    for (const field of UpdateProfileFields) {
        if (formStatus.value[field].new !== store.user[field]) {
            params.append(field, formStatus.value[field].new);
        }
    }
    await proxy.$axios.post(
        '/api/userprofile/update_profile',
        params,
    ).then((response) => {
        const data = response.data as EnumMap<UpdateProfileField, UpdateProfileResponseSingle>;
        for (const field of UpdateProfileFields) {
            processUpdateResponse(field, data[field]);
        }
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
    'en': { local: {
        englishName: 'International Name',
        englishNameTooltip: 'Fill in your given name and family name in English to let minesweepers around the world know you.',
        firstname: 'Given Name',
        lastname: 'Family Name',
        localname: 'Local Name',
        localnameTooltip: 'Fill in your full name in your local language. This field is required to upload videos.',
        realname: 'Real Name',
        realnameTooltip: 'Your real name cannot be changed once set. If you have a legitimate reason to change your name, please contact a moderator.',
        signature: 'Signature',
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
