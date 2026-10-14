<template>
    <div>
        录像ID
        <ElInputNumber v-model="videoid" :controls="false" :min="0" />
        <BaseButton @click="getVideo">
            查询
        </BaseButton>
        <BaseButton @click="previewVideo">
            播放
        </BaseButton>
        <BaseButton @click="updateVideo(videoid)">
            更新
        </BaseButton>
        <BaseButton @click="removeNewest(videoid)">
            从最新录像中移除
        </BaseButton>
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
        <BaseButton @click="setVideo(videoid, videofield, videovalue)">
            修改
        </BaseButton>
    </div>
    <ElDescriptions title="VideoModel">
        <ElDescriptionsItem v-for="(value, field) in videomodel" :key="field" :label="field">
            {{ value }}
        </ElDescriptionsItem>
    </ElDescriptions>
</template>

<script lang="ts" setup>
import type { AxiosResponse } from 'axios';
import { ElDescriptions, ElDescriptionsItem, ElInput, ElInputNumber, ElOption, ElSelect } from 'element-plus';
import { ref } from 'vue';

import BaseButton from '@/components/common/BaseButton.vue';
import { httpErrorNotification, successNotification } from '@/components/Notifications';
import { preview } from '@/utils/common/PlayerDialog';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import type { MS_Software } from '@/utils/ms_const';
import { MS_Softwares } from '@/utils/ms_const';

const { proxy } = useCurrentInstance();

const videoid = ref(0);
const videofield = ref('');
const videovalue = ref('');
const videofieldlist = ['player', 'upload_time', 'state']; // 可以修改的域列表
const videomodel = ref<Record<string, unknown>>({});
const softwareSet = new Set<unknown>(MS_Softwares);

const getVideo = () => {
    proxy.$axios.get<Record<string, unknown>>('video/get', { params: { id: videoid.value } }).then(
        function (response) {
            videomodel.value = response.data;
        },
    ).catch(httpErrorNotification);
};

function setVideoResponse(response: AxiosResponse<unknown>) {
    successNotification(response);
    getVideo();
}

const setVideo = (id: number, field: string, value: string) => {
    proxy.$axios.post<unknown>('video/set/', { id: id, field: field, value: value }).then(setVideoResponse).catch(httpErrorNotification);
};

const updateVideo = (id: number) => {
    proxy.$axios.post<unknown>('video/update/', { id: id }).then(setVideoResponse).catch(httpErrorNotification);
};

const removeNewest = (id: number) => {
    proxy.$axios.post<unknown>('video/newest_queue/remove/', { id: id }).then(setVideoResponse).catch(httpErrorNotification);
};

function previewVideo() {
    const { software } = videomodel.value;
    void preview(videoid.value, softwareSet.has(software) ? software as MS_Software : undefined);
}
</script>
