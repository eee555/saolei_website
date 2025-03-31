<template>
    批量刷新录像<br />
    开始ID<el-input-number v-model="startid" />&nbsp;
    结束ID<el-input-number v-model="endid" />&nbsp;
    批处理数量<el-input-number v-model="batchsize" />&nbsp;
    <el-button :disabled="working" @click="startBatchUpdate">开始！</el-button>
    <el-button :disabled="!working" @click="stopBatchUpdate">停止！</el-button><br />
    客户端会将需要处理的ID段按照批处理数量发送到服务器进行批处理。批处理数量越大，服务器处理效率越高，但是如果批处理数量过大，会导致连接超时。
    <el-text v-for="(log, index) in logList" :key="index" :style="{ display: 'block' }">{{ log }}</el-text>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElInputNumber, ElButton, ElText } from 'element-plus';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const { proxy } = useCurrentInstance();

const startid = ref(1);
const endid = ref(1000);
const batchsize = ref(100);

const working = ref(false);
const logList = ref<string[]>([]);

async function startBatchUpdate() {
    working.value = true;
    for (let i = startid.value; i <= endid.value; i += batchsize.value) {
        if (!working.value) {
            break;
        }
        const start = i;
        const end = Math.min(i + batchsize.value - 1, endid.value);
        logList.value.push(`${new Date().toISOString()} 正在处理${start}至${end}`);
        await proxy.$axios.post('video/update/batch/', { startid: start, endid: end }).then(
            function (response) {
                logList.value.push(`${start}至${end}已处理完成，成功${response.data.successCount}个，失败${response.data.errorList.length}个`);
                if (response.data.errorList.length > 0){
                    logList.value.push(`失败的录像为：${response.data.errorList.join('、')}`);
                }
            },
        ).catch(function (error) {
            logList.value.push(`${start}至${end}未处理完成，服务器返回错误：${error.message}`);
        });
    }
    working.value = false;
}

function stopBatchUpdate() {
    working.value = false;
}

</script>