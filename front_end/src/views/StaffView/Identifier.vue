<template>
    <ElInput v-model="identifier" />
    <ElButton @click="handleGet">
        查询
    </ElButton>
    <ElButton v-if="safe != 'unknown'" @click="handleDelete">
        删除
    </ElButton>
    <ElButton v-if="safe == 'false'" @click="handleApprove">
        通过审核
    </ElButton>
    <template v-if="userid === 0 && identifier !== ''">
        <br>&nbsp;
        绑定用户ID
        <ElInputNumber v-model="newUserid" />
        <ElButton @click="handleAdd">
            绑定
        </ElButton>
    </template>
    <br>
    用户ID: {{ userid }}，状态：{{ safe }}
</template>

<script setup lang="ts">
import { ElButton, ElInput, ElInputNumber } from 'element-plus';
import { ref } from 'vue';

import { httpErrorNotification, successNotification } from '@/components/Notifications';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const { proxy } = useCurrentInstance();

const identifier = ref('');
const safe = ref('unknown');
const userid = ref(0);
const newUserid = ref(0);

function handleGet() {
    proxy.$axios.get('identifier/get/staff/', { params: { identifier: identifier.value } }).then(
        function (response) {
            safe.value = response.data.safe.toString();
            userid.value = response.data.user;
        },
    ).catch(httpErrorNotification);
}

function handleDelete() {
    proxy.$axios.post('identifier/del/staff/', { identifier: identifier.value }).then(
        function (response) {
            identifier.value = '';
            safe.value = 'unknown';
            userid.value = 0;
            successNotification(response);
        },
    ).catch(httpErrorNotification);
}

function handleApprove() {
    proxy.$axios.post('identifier/approve/staff/', { identifier: identifier.value }).then(
        function (response) {
            safe.value = 'true';
            successNotification(response);
        },
    ).catch(httpErrorNotification);
}

function handleAdd() {
    proxy.$axios.post('identifier/add/staff/', { identifier: identifier.value, userid: newUserid.value }).then(
        function (response) {
            safe.value = 'true';
            userid.value = newUserid.value;
            successNotification(response);
        },
    ).catch(httpErrorNotification);
}
</script>
