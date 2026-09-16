<template>
    <div>
        用户ID
        <ElInputNumber v-model="userId" :controls="false" :min="1" />
        <ElButton :loading="loading" @click="loadUser">
            查询
        </ElButton>
    </div>

    <template v-if="profile">
        <VCodeBlock :code="JSON.stringify(profile, null, 2)" lang="json" highlightjs />
        UserProfile
        <ElInput v-model="userProfileRequestBody" type="textarea" :autosize="{ minRows: 8 }" />
        <ElButton type="primary" :loading="savingUserProfile" @click="saveUserProfile">
            PATCH UserProfile
        </ElButton>
        UserMS
        <ElInput v-model="userMSRequestBody" type="textarea" :autosize="{ minRows: 8 }" />
        <ElButton type="primary" :loading="savingUserMS" @click="saveUserMS">
            PATCH UserMS
        </ElButton>
    </template>
</template>

<script setup lang="ts">
import { VCodeBlock } from '@wdns/vue-code-block';
import { ElButton, ElInput, ElInputNumber } from 'element-plus';
import { ref } from 'vue';

import { actionSuccessNotification, baseErrorNotification, httpErrorNotification } from '@/components/Notifications';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const { proxy } = useCurrentInstance();

const userId = ref(1);
const loading = ref(false);
const savingUserProfile = ref(false);
const savingUserMS = ref(false);
const profile = ref<Record<string, unknown> | null>(null);
const loadedUserId = ref<number | null>(null);
const userProfileRequestBody = ref('{}');
const userMSRequestBody = ref('{}');

async function reloadUser(id: number) {
    await proxy.$axios.get<Record<string, unknown>>(`/api/userprofile/admin/detail/${id}`).then((response) => {
        profile.value = response.data;
        loadedUserId.value = id;
    });
}

async function loadUser() {
    loading.value = true;
    await reloadUser(userId.value).then(() => {
        userProfileRequestBody.value = '{}';
        userMSRequestBody.value = '{}';
    }).catch(httpErrorNotification);
    loading.value = false;
}

function parseRequestBody(body: string) {
    try {
        const data: unknown = JSON.parse(body);
        if (typeof data !== 'object' || data === null || Array.isArray(data)) {
            baseErrorNotification('JSON错误', 'request body必须是JSON object');
            return null;
        }
        return data as Record<string, unknown>;
    } catch (error) {
        baseErrorNotification('JSON错误', String(error));
        return null;
    }
}

async function saveUserProfile() {
    if (!profile.value || loadedUserId.value === null) return;

    const payload = parseRequestBody(userProfileRequestBody.value);
    if (payload === null) return;

    savingUserProfile.value = true;
    await proxy.$axios.patch<Record<string, unknown>>(`/api/userprofile/admin/update/${loadedUserId.value}`, payload).then((response) => {
        profile.value = response.data;
        userProfileRequestBody.value = '{}';
        actionSuccessNotification();
    }).catch(httpErrorNotification);
    savingUserProfile.value = false;
}

async function saveUserMS() {
    if (!profile.value || loadedUserId.value === null) return;

    const payload = parseRequestBody(userMSRequestBody.value);
    if (payload === null) return;

    const usermsId = profile.value.userms_id;
    if (typeof usermsId !== 'number') {
        baseErrorNotification('UserMS错误', '当前用户没有可用的userms_id');
        return;
    }

    const id = loadedUserId.value;
    savingUserMS.value = true;
    await proxy.$axios.patch<Record<string, unknown>>(`/api/msuser/admin/update/${usermsId}`, payload).then(async () => {
        userMSRequestBody.value = '{}';
        await reloadUser(id);
        actionSuccessNotification();
    }).catch(httpErrorNotification);
    savingUserMS.value = false;
}
</script>
