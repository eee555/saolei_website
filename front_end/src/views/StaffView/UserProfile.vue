<template>
    <div>
        用户ID
        <ElInputNumber v-model="userid" :controls="false" :min="0" />
        <ElButton @click="getUser">
            查询
        </ElButton>
    </div>
    <div>
        域<ElSelect v-model="userfield">
            <ElOption v-for="field in userfieldlist" :key="field" :value="field" />
        </ElSelect>
    </div>
    <div>
        值<ElInput v-model="uservalue" />
    </div>
    <div>
        <ElButton @click="setUser(userid, userfield, uservalue)">
            修改
        </ElButton>
    </div>
    <ElDescriptions title="UserProfile">
        <ElDescriptionsItem v-for="(value, field) in userprofile" :key="field" :label="field">
            {{ value }}
        </ElDescriptionsItem>
    </ElDescriptions>
</template>

<script setup lang="ts">
import { ElButton, ElDescriptions, ElDescriptionsItem, ElInput, ElInputNumber, ElOption, ElSelect } from 'element-plus';
import { ref } from 'vue';

import { httpErrorNotification, successNotification } from '@/components/Notifications';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const { proxy } = useCurrentInstance();

const userid = ref(0);
const userfield = ref('');
const uservalue = ref('');
const userfieldlist = ['username', 'first_name', 'last_name', 'email', 'realname', 'country', 'is_banned', 'left_realname_n', 'left_avatar_n', 'left_signature_n', 'userms__video_num_limit']; // 可以修改的域列表
const userprofile = ref({});

const getUser = () => {
    proxy.$axios.get('userprofile/get', { params: { id: userid.value } }).then(
        function (response: any) {
            userprofile.value = response.data;
        },
    ).catch(httpErrorNotification);
};

const setUser = (id: number, field: string, value: string) => {
    proxy.$axios.post('userprofile/set/', { id: id, field: field, value: value }).then(
        function (response: any) {
            successNotification(response);
            getUser();
        },
    ).catch(httpErrorNotification);
};
</script>
