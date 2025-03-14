<template>
    标识
    <el-input v-model="identifier"></el-input>
    <el-button @click="handleGet">查询</el-button>
    <el-button @click="handleDelete">删除</el-button>
    <br/>
    用户ID: {{ userid }}，状态：{{ safe }}
</template>

<script setup lang="ts">

import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { ElInput, ElButton } from 'element-plus';
import { ref } from 'vue';
import { httpErrorNotification, successNotification } from '@/components/Notifications';

const { proxy } = useCurrentInstance();

const identifier = ref("");
const safe = ref('unknown');
const userid = ref(0);

function handleGet() {
    proxy.$axios.get('identifier/get/staff/', {params: {identifier: identifier.value}}).then(
        function (response) {
            safe.value = response.data.safe.toString();
            userid.value = response.data.user;
        }
    ).catch(httpErrorNotification);
}

function handleDelete() {
    proxy.$axios.post('identifier/del/staff/', {identifier: identifier.value}).then(
        function (response) {
            identifier.value = "";
            safe.value = 'unknown';
            userid.value = 0;
            successNotification(response);
        }
    ).catch(httpErrorNotification)
}

</script>