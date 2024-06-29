<template>
    <el-upload v-model:file-list="fileList" :disabled="store.user.realname == '匿名'" ref="upload" drag action="#"
        :multiple="true" :on-change="handleChange" :auto-upload="false" :show-file-list="false" accept=".avf,.evf">

        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text" style="font-size: 18px;"
            v-html="store.user.realname == '匿名' ? $t('common.msg.realNameRequired') : $t('profile.upload.dragOrClick')">
        </div>

        <template #tip>

            <div class="el-upload__tip text-red" style="background-color: white;text-align: center;">
                <el-button @click="submitUpload()" size="large" type="primary" v-show="video_msgs.length > 0"
                    style="display: block;margin: 16px auto;font-size: 18px;width: 220px;">{{ $t('profile.upload.uploadAll', [video_msgs.length]) }}</el-button>
                <el-button @click="cancel_all()" size="small" type="info" v-show="video_msgs.length > 0"
                    style="display: block;margin: 16px auto;width: 120px;" plain>{{ $t('profile.upload.cancelAll') }}</el-button>
                <span style="font-size: 14px;">{{ $t('profile.upload.constraintNote') }}</span>
            </div>
        </template>
    </el-upload>
    <el-table :data="video_msgs" table-layout="auto">
        <el-table-column type="expand">
            <template #default="props">
                <el-descriptions>
                    <el-descriptions-item :label="$t('common.prop.fileName')">{{ props.row.filename }}</el-descriptions-item>
                    <el-descriptions-item v-if="props.row.videostat != null" :label="$t('common.prop.designator')">{{
                        props.row.videostat.designator }}</el-descriptions-item>
                    <el-descriptions-item v-if="props.row.videostat != null" v-for="key in extfields" :label="key">{{
                        props.row.extstat[key] }}</el-descriptions-item>
                </el-descriptions>
            </template>
        </el-table-column>
        <el-table-column prop="videostat.level" :label="$t('common.prop.level')" sortable>
            <template #default="props">
                {{ $t('common.level.' + props.row.videostat.level) }}
            </template>
        </el-table-column>
        <el-table-column prop="videostat.timems" :label="$t('common.prop.time')" sortable></el-table-column>
        <el-table-column prop="videostat.bbbv" label="3BV" sortable></el-table-column>
        <el-table-column prop="videostat.bvs" label="3BV/s" sortable></el-table-column>
        <el-table-column :label="$t('common.prop.status')" sortable sort-by="status">
            <template #default="props">
                {{ $t('profile.upload.error.' + props.row.status) }}
            </template>
        </el-table-column>
        <el-table-column :label="$t('common.prop.action')">
            <template #default="props">
                <el-button :disabled="props.row.status != 'designator' && props.row.status != 'pass'"
                    @click="forceUpload(props.$index)"
                    :type="props.row.status == 'pass' ? 'success' : props.row.status == 'designator' ? 'warning' : 'info'"
                    circle><el-icon>
                        <Upload />
                    </el-icon></el-button>
                <el-button @click="removeUpload(props.$index)" type="danger" circle><el-icon>
                        <Delete />
                    </el-icon></el-button>
            </template>
        </el-table-column>
    </el-table>
</template>

<script lang="ts" setup>
// 上传录像的页面
import { ref } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
import type { UploadInstance, UploadProps, UploadUserFile, UploadRawFile, UploadFile, UploadFiles, UploadRequestOptions } from 'element-plus'
// import img_arbiter from '@/assets/img/img_arbiter.png'
import { useUserStore } from '../store'
const store = useUserStore()

import { useI18n } from 'vue-i18n';
const t = useI18n();

const data = defineProps({
    designators: { type: Array, default: () => [] }
})

const extfields = ['left', 'right', 'double', 'cl', 'left_s', 'right_s', 'double_s', 'cl_s', 'path', 'flag', 'flag_s', 'stnb', 'rqp', 'ioe', 'thrp', 'corr', 'ce', 'ce_s', 'op', 'isl', 'cell0', 'cell1', 'cell2', 'cell3', 'cell4', 'cell5', 'cell6', 'cell7', 'cell8']

interface ExtendedVideoStat {
    left: number,
    right: number,
    double: number,
    cl: number,
    left_s: number,
    right_s: number,
    double_s: number,
    cl_s: number,
    path: number,
    flag: number,
    flag_s: number,
    stnb: number,
    rqp: number,
    ioe: number,
    thrp: number,
    corr: number,
    ce: number,
    ce_s: number,
    op: number,
    isl: number,
    cell0: number,
    cell1: number,
    cell2: number,
    cell3: number,
    cell4: number,
    cell5: number,
    cell6: number,
    cell7: number,
    cell8: number,
}

interface VideoStat {
    level: string,
    mode: string,
    timems: number,
    bbbv: number,
    bvs: number,
    designator: string,
    review_code: number,
}

interface GeneralFile {
    uid: number,
    id: number,
    filename: string,
    file: File,
    status: string,
    videostat: VideoStat | null,
    extstat: ExtendedVideoStat | null,
}

const video_msgs = ref<GeneralFile[]>([])

const fileList = ref<UploadUserFile[]>([])

const upload = ref<UploadInstance>();
const uploaded_file_num = ref<number>(0);
const allow_upload = ref(true)

// 延时系数
let k = 0;

// 录像列表变动的回调，上传多个文件时，有几个文件就会进来几次。
const handleChange: UploadProps['onChange'] = async (uploadFile: UploadFile, uploadFiles: UploadFiles) => {

    if (allow_upload.value) {
        // upload_video_visible.value = true;
        await push_video_msg(uploadFile);
        // 修改id。最后一个协程才是真正起作用的。
        for (let i = 0; i < video_msgs.value.length; i++) {
            video_msgs.value[i].id = i;
        }
    }

}

// 新增一条等待上传的录像信息的记录
const push_video_msg = async (uploadFile: UploadFile | UploadRawFile) => {
    const ms = await import("ms-toollib");
    let uid = uploadFile.uid;
    let id = 0;
    let status = "pass";
    let video_file;
    let video_stat;
    let ext_stat;
    if ("raw" in uploadFile) {
        video_file = uploadFile.raw as UploadRawFile;
    } else {
        video_file = uploadFile as UploadRawFile;
    }
    let video_file_u8 = new Uint8Array(await video_file.arrayBuffer());
    let aa;
    if (uploadFile.name.slice(-3) == "avf") {
        aa = ms.AvfVideo.new(video_file_u8, uploadFile.name);
    } else if (uploadFile.name.slice(-3) == "evf") {
        aa = ms.EvfVideo.new(video_file_u8, uploadFile.name);
    } else {
        aa = null
        status = "fileext";
    }
    const decoder = new TextDecoder();
    if (aa != null) {
        aa.parse_video();
        aa.analyse();
        aa.current_time = 1e8; //时间设置到最后（超出就是最后）
        video_stat = {
            level: ["b", "i", "e", "c"][aa.get_level - 3],
            mode: String(aa.get_mode).padStart(2, '0'),
            timems: aa.get_rtime_ms,
            bbbv: aa.get_bbbv,
            bvs: aa.get_bbbv_s,
            designator: decoder.decode(aa.get_player_designator),
            review_code: aa.is_valid(),
        }
        ext_stat = get_ext_stat(aa)
        if (video_stat.level == "c") {
            status = "custom";
        } else if (uploadFile.name.length >= 100) {
            status = "filename";
        } else if (!data.designators.includes(video_stat.designator)) {
            status = "designator";
        }

    } else {
        video_stat = null;
        ext_stat = null;
    }

    video_msgs.value.push({
        uid: uploadFile.uid,
        id: 0,
        filename: uploadFile.name,
        file: video_file,
        status: status,
        videostat: video_stat,
        extstat: ext_stat,
    })
}

// 清空待上传列表
const cancel_all = () => {
    upload.value!.clearFiles();
    while (video_msgs.value.length > 0) {
        video_msgs.value.pop();
    }
    uploaded_file_num.value = 0;
    k = 0;
}

// 点上传按钮的回调，自动上传录像
const submitUpload = async () => {
    // 先锁死，不让进变化回调
    allow_upload.value = false;
    let i = 0;
    let count = 0; // 最多上传99个
    while (count < 99) {
        if (i >= video_msgs.value.length) break;
        if (video_msgs.value[i].status === "pass") {
            await forceUpload(i);
            count++;
            continue;
        }
        i++;
    }
    allow_upload.value = true;
}

// 上传问题不大的录像
const forceUpload = async (i: number) => {
    let video = video_msgs.value[i];
    if (video.status != "pass" && video.status != "designator") {
        return;
    }
    video_msgs.value[i].status = "process";
    await getDelay();
    if (video.videostat == null || video.extstat == null) {
        video_msgs.value[i].status = "upload";
        return;
    }
    let params = new FormData();
    params.append('file', video.file);
    params.append('review_code', video.videostat.review_code.toString());
    params.append("software", ["e", "a"][video.filename.slice(-3) == "avf" ? 1 : 0]);
    params.append("level", video.videostat.level);
    params.append("mode", video.videostat.mode);
    params.append("timems", video.videostat.timems.toString());
    params.append("bv", video.videostat.bbbv.toString());
    params.append("bvs", video.videostat.bvs.toString());
    params.append("designator", video.videostat.designator);
    for (let prop of extfields) {
        params.append(prop, video.extstat[prop].toString());
    }
    await proxy.$axios.post('/video/upload/',
        params,
    ).then(function (response) {
        if (response.status == 200) {
            uploaded_file_num.value += 1;
            removeUpload(i);
        } else {
            // 正常使用不会到这里
            video_msgs.value[i].status = "upload";
        }
    }).catch((error: any) => {
        if (error.response.status == 409) {
            video_msgs.value[i].status = "collision";
        } else {
            video_msgs.value[i].status = "upload";
        }
    })
}

//删除录像
const removeUpload = (i: number) => {
    video_msgs.value.splice(i, 1);
}

// 均匀延时，降低并发。
function getDelay() {
    return new Promise(resolve => {
        const delay = 200;
        k++;
        setTimeout(() => {
            resolve(delay);
        }, delay);
    });
}

const get_ext_stat = (aa: any) => {
    return {
        left: aa.get_left,
        right: aa.get_right,
        double: aa.get_double,
        cl: aa.get_cl,
        left_s: aa.get_left_s,
        right_s: aa.get_right_s,
        double_s: aa.get_double_s,
        cl_s: aa.get_cl_s,
        path: aa.get_path,
        flag: aa.get_flag,
        flag_s: aa.get_flag_s,
        stnb: aa.get_stnb,
        rqp: aa.get_rqp,
        ioe: aa.get_ioe,
        thrp: aa.get_thrp,
        corr: aa.get_corr,
        ce: aa.get_ce,
        ce_s: aa.get_ce_s,
        op: aa.get_op,
        isl: aa.get_isl,
        cell0: aa.get_cell0,
        cell1: aa.get_cell1,
        cell2: aa.get_cell2,
        cell3: aa.get_cell3,
        cell4: aa.get_cell4,
        cell5: aa.get_cell5,
        cell6: aa.get_cell6,
        cell7: aa.get_cell7,
        cell8: aa.get_cell8,
    }
}

</script>


<style>
/* input:invalid {
    outline: 2px solid rgb(167, 11, 11);
    border-radius: 3px;
} */

.upload_video {
    font-size: 20px;
    border-radius: 8px;
    border: 1px dashed rgb(120, 120, 120);
    width: 61%;
    margin: auto;
    margin-top: 10px;
    padding: 12px;
    background-color: rgb(244, 244, 244);
    text-align: center;
}

.el-row {
    margin-bottom: 0px;
}

.el-row:last-child {
    margin-bottom: 0;
}

.card_fade-move,
.card_fade-enter-active,
.card_fade-leave-active {
    transition: all 0.5s ease;
}

.card_fade-enter-from,
.card_fade-leave-to {
    opacity: 0;
    transform: translateX(200px);
}

.card_fade-leave-active {
    position: absolute;
}
</style>
