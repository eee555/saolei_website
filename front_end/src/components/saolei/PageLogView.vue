<template>
    <el-timeline>
        <el-timeline-item v-for="baseLog of data.videoLogs" :key="baseLog.time.toISOString()" :timestamp="toISODateTimeString(baseLog.time)" :type="typeMap[baseLog.type]" :size="sizeMap[baseLog.type]">
            <el-text v-if="baseLog.type === 'consoleError'">
                发生严重错误！
                <el-button @click="handleConsoleLog(baseLog.error)">
                    输出到控制台
                </el-button>
            </el-text>
            <el-text v-else-if="baseLog.type === 'videoStart'">
                开始导入录像#{{ data.videoList[baseLog.videoIndex!].id }}
                <SaoleiVideoView :video="data.videoList[baseLog.videoIndex!]" />
            </el-text>
            <el-text v-else-if="baseLog.type === 'videoSuccess'">
                录像#{{ data.videoList[baseLog.videoIndex!].id }}导入完成！
                <el-button @click="preview(data.videoList[baseLog.videoIndex!].import_video!)">
                    播放
                </el-button>
            </el-text>
            <el-text v-else-if="baseLog.type === 'videoError'">
                录像#{{ data.videoList[baseLog.videoIndex!].id }}导入失败！{{ t(`errorMsg.${baseLog.error.object}.title`) }}
                <br>
                {{ t(`errorMsg.${baseLog.error.object}.${baseLog.error.category}`) }}
            </el-text>
            <el-text v-else-if="baseLog.type === 'videoListStart'">
                <template v-if="data.index === 0">
                    开始获取未导入的录像
                </template>
                <template v-else>
                    开始获取第{{ data.index }}页录像列表
                </template>
            </el-text>
            <el-text v-else-if="baseLog.type === 'videoListFinish'">
                录像列表获取完成！准备导入{{ data.videoList.length }}条录像
            </el-text>
            <el-text v-else-if="baseLog.type === 'videoListError'">
                录像列表获取失败！
            </el-text>
            <el-text v-else-if="baseLog.type === 'pageEnd'">
                <template v-if="data.index === 0">
                    未导入的录像全部导入完成！
                </template>
                <template v-else>
                    第{{ data.index }}页录像导入完成！
                </template>
            </el-text>
        </el-timeline-item>
    </el-timeline>
</template>

<script setup lang="ts">
import { ElButton, ElText, ElTimeline, ElTimelineItem } from 'element-plus';
import { useI18n } from 'vue-i18n';

import { PageLog } from './importLog';
import SaoleiVideoView from './SaoleiVideoView.vue';

import { preview } from '@/utils/common/PlayerDialog';
import { toISODateTimeString } from '@/utils/datetime';

const { t } = useI18n();

defineProps({
    data: {
        type: PageLog,
        required: true,
    },
});

const typeMap = {
    consoleError: 'danger',
    videoStart: 'primary',
    videoSuccess: 'success',
    videoError: 'warning',
    videoListStart: 'primary',
    videoListFinish: 'success',
    videoListError: 'warning',
    pageEnd: 'info',
} as const;

const sizeMap = {
    consoleError: 'large',
    videoStart: 'large',
    videoSuccess: 'normal',
    videoError: 'normal',
    videoListStart: 'normal',
    videoListFinish: 'large',
    videoListError: 'normal',
    pageEnd: 'normal',
} as const;

function handleConsoleLog(error: any) {
    console.log(error);
}
</script>
