<template>
    <div>
        用户ID
        <el-input-number v-model="userid" :controls="false" :min="0" />
        <el-button @click="getUser">
            查询
        </el-button>
    </div>
    <div>
        域<el-select v-model="userfield">
            <el-option v-for="field in userfieldlist" :key="field" :value="field" />
        </el-select>
    </div>
    <div>
        值<el-input v-model="uservalue" />
    </div>
    <div>
        <el-button @click="setUser(userid, userfield, uservalue)">
            修改
        </el-button>
    </div>
    <el-descriptions title="UserProfile">
        <el-descriptions-item v-for="(value, field) in userprofile" :key="field" :label="field">
            {{ value }}
        </el-descriptions-item>
    </el-descriptions>
</template>

<script setup lang="ts">
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { httpErrorNotification, successNotification } from '../Notifications';
import { ref } from 'vue';
import { ElInput, ElInputNumber, ElButton, ElDescriptions, ElDescriptionsItem, ElSelect, ElOption } from 'element-plus';

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
