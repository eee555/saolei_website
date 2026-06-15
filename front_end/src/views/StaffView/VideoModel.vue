<template>
    <div>
        录像ID
        <ElInputNumber v-model="videoid" :controls="false" :min="0" />
        <ElButton @click="getVideo">
            查询
        </ElButton>
        <ElButton @click="preview(videoid)">
            播放
        </ElButton>
        <ElButton @click="updateVideo(videoid)">
            更新
        </ElButton>
        <ElButton @click="removeNewest(videoid)">
            从最新录像中移除
        </ElButton>
    </div>
    <div>
        域<ElSelect v-model="videofield">
            <ElOption v-for="field in videofieldlist" :key="field" :value="field" />
        </ElSelect>
    </div>
    <div>
        值<ElInput v-model="videovalue" />
    </div>
    <div>
        <ElButton @click="setVideo(videoid, videofield, videovalue)">
            修改
        </ElButton>
    </div>
    <ElDescriptions title="VideoModel">
        <ElDescriptionsItem v-for="(value, field) in videomodel" :key="field" :label="field">
            {{ value }}
        </ElDescriptionsItem>
    </ElDescriptions>
</template>

<script lang="ts" setup>
import { ElButton, ElDescriptions, ElDescriptionsItem, ElInput, ElInputNumber, ElOption, ElSelect } from 'element-plus';
import { ref } from 'vue';

import { httpErrorNotification, successNotification } from '@/components/Notifications';
import { preview } from '@/utils/common/PlayerDialog';
import useCurrentInstance from '@/utils/common/useCurrentInstance';


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

const removeNewest = (id: number) => {
    proxy.$axios.post('video/newest_queue/remove/', { id: id }).then(setVideoResponse).catch(httpErrorNotification);
};
</script>
