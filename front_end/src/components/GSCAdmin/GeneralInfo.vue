<template>
    <el-text v-if="id === 0">
        请输入非零届数
    </el-text>
    <el-text v-else-if="notFound">
        未找到该届信息
        <el-button @click="createGSC">
            创建比赛
        </el-button>
    </el-text>
    <el-text v-else-if="loadingGSCInfo">
        正在加载信息...
    </el-text>
    <el-text v-else>
        开始时间：{{ gscInfo.start_time ? gscInfo.start_time.toLocaleString() : '未设置' }}
        &nbsp;
        设置开始时间：
        <el-date-picker v-model="newStartTime" type="datetime" @change="setStartTime" />
        <br>
        结束时间：{{ gscInfo.end_time ? gscInfo.end_time.toLocaleString() : '未设置' }}
        &nbsp;
        设置结束时间：
        <el-date-picker v-model="newEndTime" type="datetime" @change="setEndTime" />
        <br>
        标识：{{ gscInfo.token || '未设置' }}
        &nbsp;
        设置标识：
        <el-input v-model="newToken" @change="setToken" />
    </el-text>
</template>

<script setup lang="ts">
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { GSCInfo } from '@/utils/gsc';
import { ref, watch } from 'vue';
import { httpErrorNotification, successNotification } from '../Notifications';
import { ElText, ElDatePicker, ElInput, ElButton } from 'element-plus';


const props = defineProps({
    id: { type: Number, default: 0 },
});

watch(() => props.id, (newId) => {
    if (newId > 0) {
        getGSCInfo(newId);
    }
}, { immediate: true });

const { proxy } = useCurrentInstance();
const gscInfo = ref<GSCInfo>({ id: 0 });
const newStartTime = ref<Date | undefined>(undefined);
const newEndTime = ref<Date | undefined>(undefined);
const newToken = ref<string>('');
const loadingGSCInfo = ref(false);
const notFound = ref(false);

async function getGSCInfo(id: number | undefined) {
    if (id === undefined || id < 1) {
        gscInfo.value = { id: 0 };
        return;
    }
    loadingGSCInfo.value = true;
    notFound.value = false;
    await proxy.$axios.get('tournament/get_gsc_tournament/', { params: { id: id } }).then(
        function (response: any) {
            if (response.data.type === 'error') {
                notFound.value = true;
            }
            if (response.data.data.start_time) {
                gscInfo.value.start_time = new Date(response.data.data.start_time);
            }
            if (response.data.data.end_time) {
                gscInfo.value.end_time = new Date(response.data.data.end_time);
            }
            if (response.data.data.token) {
                gscInfo.value.token = response.data.token;
            }
            gscInfo.value.id = response.data.data.id;
        },
    ).catch(httpErrorNotification);
    loadingGSCInfo.value = false;
}

function createGSC() {
    proxy.$axios.post('tournament/new_gsc/', { id: props.id }).then(
        function (response: any) {
            successNotification(response);
            getGSCInfo(props.id);
        },
    ).catch(httpErrorNotification);
}

function setStartTime(time: Date | undefined) {
    if (time === undefined) return;
    console.log(gscInfo.value);
    proxy.$axios.post('tournament/set/', { id: gscInfo.value.id, start_time: time }).then(
        function (response: any) {
            gscInfo.value.start_time = time;
            newStartTime.value = undefined;
            successNotification(response);
        },
    ).catch(httpErrorNotification);
}

function setEndTime(time: Date | undefined) {
    if (time === undefined) return;
    proxy.$axios.post('tournament/set/', { id: gscInfo.value.id, end_time: time }).then(
        function (response: any) {
            gscInfo.value.end_time = time;
            newEndTime.value = undefined;
            successNotification(response);
        },
    ).catch(httpErrorNotification);
}

function setToken(token: string) {
    if (token === undefined || token.trim() === '') return;
    proxy.$axios.post('tournament/set/', { id: gscInfo.value.id, token: token }).then(
        function (response: any) {
            gscInfo.value.token = token;
            successNotification(response);
        },
    ).catch(httpErrorNotification);
}

</script>
