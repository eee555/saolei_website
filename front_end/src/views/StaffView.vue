<template>
    <div>
        用户ID
        <el-input-number v-model="userid" :controls="false" :min="0"></el-input-number>
        <el-button @click="getUser">查询</el-button>
    </div>
    <div>
        域<el-select v-model="userfield">
            <el-option v-for="field in descriptionitems" :value="field"></el-option>
        </el-select>
    </div>
    <div>
        值<el-input v-model="uservalue"></el-input>
    </div>
    <div>
        <el-button @click="setUser(userid, userfield, uservalue)">修改</el-button>
    </div>
    <el-descriptions title="UserProfile">
        <el-descriptions-item v-for="item in descriptionitems" :label="item">{{ userprofile[item] }}</el-descriptions-item>
    </el-descriptions>
</template>

<script lang="ts" setup>

import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { generalNotification } from '@/utils/system/status';
import { UserProfile } from '@/utils/common/structInterface';
import { ref } from 'vue';

import { useI18n } from 'vue-i18n';
const t = useI18n();

const { proxy } = useCurrentInstance();

const userid = ref(0);
const userfield = ref("");
const uservalue = ref("");
const descriptionitems = ["username", "first_name", "last_name", "email", "realname", "country", "is_banned", "left_realname_n", "left_avatar_n", "left_signature_n"]

const userprofile = ref<UserProfile>({
    userms__designators: [],
    userms__video_num_limit: 0,
    username: "",
    first_name: "",
    last_name: "",
    email: "",
    realname: "",
    signature: "",
    country: "",
    is_banned: false,
    left_realname_n: 0,
    left_avatar_n: 0,
    left_signature_n: 0,
});

const getUser = () => {
    proxy.$axios.get('userprofile/get', {params: {id: userid.value}}).then(
        function (response: any) {
            userprofile.value = response.data;
        }
    ).catch(error => {
        generalNotification(t, error.response.status, t.t('common.action.getUserProfile'))
    })
}

const setUser = (id: number, field: string, value: string) => {
    proxy.$axios.post('userprofile/set/', {id: id, field: field, value: value}).then(
        function (response: any) {
            generalNotification(t, response.status, t.t('common.action.setUserProfile'));
            getUser();
        }
    )
}

</script>