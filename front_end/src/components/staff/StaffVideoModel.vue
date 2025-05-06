<template>
    <div>
        录像ID
        <el-input-number v-model="videoid" :controls="false" :min="0" />
        <el-button @click="getVideo">
            查询
        </el-button>
        <el-button @click="preview(videoid)">
            播放
        </el-button>
        <el-button @click="updateVideo(videoid)">
            更新
        </el-button>
    </div>
    <div>
        域<el-select v-model="videofield">
            <el-option v-for="field in videofieldlist" :key="field" :value="field" />
        </el-select>
    </div>
    <div>
        值<el-input v-model="videovalue" />
    </div>
    <div>
        <el-button @click="setVideo(videoid, videofield, videovalue)">
            修改
        </el-button>
    </div>
    <el-descriptions title="VideoModel">
        <el-descriptions-item v-for="(value, field) in videomodel" :key="field" :label="field">
            {{ value }}
        </el-descriptions-item>
    </el-descriptions>
</template>

<script lang="ts" setup>
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { ref } from 'vue';
import { httpErrorNotification, successNotification } from '../Notifications';
import { ElInputNumber, ElButton, ElDescriptions, ElDescriptionsItem, ElSelect, ElOption, ElInput } from 'element-plus';
import { preview } from '@/utils/common/PlayerDialog';


const { proxy } = useCurrentInstance();

const videoid = ref(0);
const videofield = ref('');
const videovalue = ref('');
const videofieldlist = ['player', 'upload_time', 'state']; // 可以修改的域列表
const videomodel = ref({});

const getVideo = () => {
    proxy.$axios.get('video/get', { params: { id: videoid.value } }).then(
        function (response: any) {
            videomodel.value = response.data;
        },
    ).catch(httpErrorNotification);
};

function setVideoResponse(response: any) {
    successNotification(response);
    getVideo();
}

const setVideo = (id: number, field: string, value: string) => {
    proxy.$axios.post('video/set/', { id: id, field: field, value: value }).then(setVideoResponse).catch(httpErrorNotification);
};

const updateVideo = (id: number) => {
    proxy.$axios.post('video/update/', { id: id }).then(setVideoResponse).catch(httpErrorNotification);
};

</script>
