<template>
    <el-text v-if="id === 0">
        请输入非零届数
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
import { ElText } from 'element-plus';


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

async function getGSCInfo(id: number | undefined) {
    if (id === undefined || id < 1) {
        gscInfo.value = { id: 0 };
        return;
    }
    loadingGSCInfo.value = true;
    await proxy.$axios.get('gsc/info', { params: { id: id } }).then(
        function (response: any) {
            if (response.data.start_time) {
                gscInfo.value.start_time = new Date(response.data.start_time);
            }
            if (response.data.end_time) {
                gscInfo.value.end_time = new Date(response.data.end_time);
            }
            if (response.data.token) {
                gscInfo.value.token = response.data.token;
            }
        },
    ).catch(httpErrorNotification);
    loadingGSCInfo.value = false;
}

function setStartTime(time: Date | undefined) {
    if (time === undefined) return;
    proxy.$axios.post('gsc/set', { id: gscInfo.value.id, field: 'start_time', value: time }).then(
        function (response: any) {
            gscInfo.value.start_time = time;
            newStartTime.value = undefined;
            successNotification(response);
        },
    ).catch(httpErrorNotification);
}

function setEndTime(time: Date | undefined) {
    if (time === undefined) return;
    proxy.$axios.post('gsc/set', { id: gscInfo.value.id, field: 'end_time', value: time }).then(
        function (response: any) {
            gscInfo.value.end_time = time;
            newEndTime.value = undefined;
            successNotification(response);
        },
    ).catch(httpErrorNotification);
}

function setToken(token: string) {
    if (token === undefined || token.trim() === '') return;
    proxy.$axios.post('gsc/set', { id: gscInfo.value.id, field: 'token', value: token }).then(
        function (response: any) {
            gscInfo.value.token = token;
            successNotification(response);
        },
    ).catch(httpErrorNotification);
}

</script>
