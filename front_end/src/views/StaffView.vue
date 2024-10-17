<template>
    <div>
        用户ID
        <el-input-number v-model="userid" :controls="false" :min="0"></el-input-number>
        <el-button @click="getUser">查询</el-button>
    </div>
    <div>
        域<el-select v-model="userfield">
            <el-option v-for="field in userfieldlist" :value="field"></el-option>
        </el-select>
    </div>
    <div>
        值<el-input v-model="uservalue"></el-input>
    </div>
    <div>
        <el-button @click="setUser(userid, userfield, uservalue)">修改</el-button>
    </div>
    <el-descriptions title="UserProfile">
        <el-descriptions-item v-for="(value, field) in userprofile" :label="field">{{ value }}</el-descriptions-item>
    </el-descriptions>
    <el-divider />
    <div>
        录像ID
        <el-input-number v-model="videoid" :controls="false" :min="0"></el-input-number>
        <el-button @click="getVideo">查询</el-button>
        <el-button @click="preview(videoid)">播放</el-button>
    </div>
    <div>
        域<el-select v-model="videofield">
            <el-option v-for="field in videofieldlist" :value="field"></el-option>
        </el-select>
    </div>
    <div>
        值<el-input v-model="videovalue"></el-input>
    </div>
    <div>
        <el-button @click="setVideo(videoid, videofield, videovalue)">修改</el-button>
    </div>
    <el-descriptions title="VideoModel">
        <el-descriptions-item v-for="(value, field) in videomodel" :label="field">{{ value }}</el-descriptions-item>
    </el-descriptions>
    <el-divider />
    <StaffAccountLink />
</template>

<script lang="ts" setup>
// 管理员操作接口，通过'/staff'访问

import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { ref } from 'vue';
import { preview } from '@/utils/common/PlayerDialog';
import StaffAccountLink from '@/components/staff/StaffAccountLink.vue';
import { httpErrorNotification, successNotification } from '@/components/Notifications';

const { proxy } = useCurrentInstance();

const userid = ref(0);
const userfield = ref("");
const uservalue = ref("");
const userfieldlist = ["username", "first_name", "last_name", "email", "realname", "country", "is_banned", "left_realname_n", "left_avatar_n", "left_signature_n", "userms__video_num_limit"]; // 可以修改的域列表
const userprofile = ref({});

const getUser = () => {
    proxy.$axios.get('userprofile/get', {params: {id: userid.value}}).then(
        function (response: any) {
            userprofile.value = response.data;
        }
    ).catch(httpErrorNotification)
}

const setUser = (id: number, field: string, value: string) => {
    proxy.$axios.post('userprofile/set/', {id: id, field: field, value: value}).then(
        function (response: any) {
            successNotification(response);
            getUser();
        }
    ).catch(httpErrorNotification)
}

const videoid = ref(0);
const videofield = ref("");
const videovalue = ref("");
const videofieldlist = ["player", "upload_time", "state"]; // 可以修改的域列表
const videomodel = ref({});

const getVideo = () => {
    proxy.$axios.get('video/get', {params: {id: videoid.value}}).then(
        function (response: any) {
            videomodel.value = response.data;
        }
    ).catch(httpErrorNotification)
}

const setVideo = (id: number, field: string, value: string) => {
    proxy.$axios.post('video/set/', {id: id, field: field, value: value}).then(
        function (response: any) {
            successNotification(response);
            getVideo();
        }
    ).catch(httpErrorNotification)
}

</script>