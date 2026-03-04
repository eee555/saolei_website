<template>
    <el-row justify="center" align="middle" style="margin-top: 1em">
        <el-text>
            页码范围
            &nbsp;
            <el-input-number v-model="startPage" :min="1" :max="endPage" :disabled="running" size="small" style="width: 7em" />
            &nbsp;
            <el-input-number v-model="endPage" :min="startPage" :disabled="running" size="small" style="width: 7em" />
        </el-text>
        <!--
        <span style="margin-left: 1em" />
        失败重试次数
        &nbsp;
        <el-input-number v-model="retryCount" :min="0" size="small" style="width: 6em" />
        -->
    </el-row>
    <el-row justify="center">
        <el-checkbox v-model="checkUnimportedVideos" :disabled="running">
            检查以往未导入的录像并导入
        </el-checkbox>
        &nbsp;
        <el-checkbox v-model="dontImportNewVideos" :disabled="running">
            仅将新录像加入队列，不导入新录像
        </el-checkbox>
    </el-row>
    <el-row justify="center">
        <el-button :disabled="running" size="large" @click="importAll">
            开始
        </el-button>
        <el-button :disabled="stopping || !running" size="large" @click="stopping = true">
            终止
        </el-button>
        <el-button :disabled="running" size="large" @click="$emit('back')">
            返回上级
        </el-button>
    </el-row>
    <el-row style="height: 1em" />
    <el-carousel
        v-if="!ArrayUtils.isEmpty(fullLog.pageLogs)" v-loading="stopping" :autoplay="false" trigger="click"
        :initial-index="fullLog.pageIndex" type="card" :loop="false" height="15rem"
    >
        <el-carousel-item v-for="pageLog of fullLog.pageLogs" :key="pageLog.index" :name="pageLog.index.toString()">
            <base-card-normal style="height: 100%; overflow-y: auto;">
                <h3 v-if="pageLog.state === 'empty'" class="justify-center small" text="2xl">
                    第{{ pageLog.index }}页无录像可导入
                </h3>
                <PageLogView v-if="pageLog.state !== 'empty'" :data="pageLog" />
            </base-card-normal>
        </el-carousel-item>
    </el-carousel>
</template>

<script setup lang="ts">
import { ElButton, ElCarousel, ElCarouselItem, ElCheckbox, ElInputNumber, ElRow, ElText, vLoading } from 'element-plus';
import { ref } from 'vue';

import { ImportLog } from './importLog';
import PageLogView from './PageLogView.vue';
import { saoleiVideoFromResponse } from './utils';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { sleep } from '@/utils';
import { ArrayUtils } from '@/utils/arrays';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const { proxy } = useCurrentInstance();

const props = defineProps({
    userId: {
        type: Number,
        required: true,
    },
});

const startPage = ref(1);
const endPage = ref(1000);
const running = ref(false);
const stopping = ref(false);
const fullLog = ref<ImportLog>(new ImportLog());
const dontImportNewVideos = ref(false);
const checkUnimportedVideos = ref(true);
// const retryCount = ref(1);

async function importVideo() {
    fullLog.value.videoStart();
    const video = fullLog.value.getCurrentVideo();
    if (!video) return;
    await proxy.$axios.post('accountlink/saolei/importvideo/', {
        video_id: video.id,
    }).then((response) => {
        const data = response.data;
        if (data.type === 'success') {
            fullLog.value.videoSuccess(saoleiVideoFromResponse(data.data));
        } else {
            fullLog.value.videoError(data.object, data.category);
        }
    }).catch((error) => {
        fullLog.value.consoleError(error);
    });
}

async function importVideoList() {
    fullLog.value.videoListStart();
    await proxy.$axios.post('accountlink/saolei/importlist/', {
        user_id: props.userId,
        page: fullLog.value.getCurrentPageLog().index,
    }).then((response) => {
        const data = response.data;
        if (data.type === 'success') {
            fullLog.value.videoListFinish(data.data.map((item: any) => saoleiVideoFromResponse(item)));
        } else {
            fullLog.value.videoListError(data.object, data.category);
        }
    }).catch((error) => {
        fullLog.value.consoleError(error);
    });
}

async function importPage(pageNumber: number) {
    fullLog.value.newPage(pageNumber);
    const pageLog = fullLog.value.getCurrentPageLog();
    await importVideoList();
    if (stopping.value) handleStop();
    await sleep(500);
    if (dontImportNewVideos.value && pageNumber) return;
    while (true) {
        if (stopping.value) handleStop();
        if (pageLog.isFinished()) break;
        await importVideo();
        await sleep(500);
    }
}

async function importAll() {
    running.value = true;
    fullLog.value = new ImportLog();
    if (checkUnimportedVideos.value) {
        await importPage(0);
    }
    while (true) {
        if (stopping.value) handleStop();
        if (startPage.value > endPage.value) handleStop();
        if (fullLog.value.isFinished()) break;
        await importPage(startPage.value);
        startPage.value += 1;
    }
    running.value = false;
}

function handleStop() {
    fullLog.value.terminate();
    stopping.value = false;
}

defineEmits(['back']);

</script>
