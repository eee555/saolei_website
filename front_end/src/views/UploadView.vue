<template>
    <el-upload v-model:file-list="fileList" :disabled="store.user.realname == '匿名'" ref="upload" drag action="#"
        :multiple="true" :on-change="handleChange" :auto-upload="false" :show-file-list="false" accept=".avf,.evf">

        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text" style="font-size: 18px;"
            v-html="store.user.realname == '匿名' ? t('common.msg.realNameRequired') : t('profile.upload.dragOrClick')">
        </div>

        <template #tip>
            <div style="text-align: center;">
                <el-button @click="submitUpload()" size="large" type="primary" v-show="upload_queue.length > 0"
                    style="display: block;margin: 16px auto;font-size: 18px;width: 220px;">{{
                        t('profile.upload.uploadAll', [upload_queue.length]) }}</el-button>
                <el-button @click="cancel_all()" size="small" type="info" v-show="upload_queue.length > 0"
                    style="display: block;margin: 16px auto;width: 120px;">{{ t('profile.upload.cancelAll')
                    }}</el-button>
                <span style="font-size: 14px;">{{ t('profile.upload.constraintNote') }}</span>
            </div>
        </template>
    </el-upload>
    <el-table :data="upload_queue" table-layout="auto">
        <el-table-column type="expand">
            <template #default="props">
                <el-descriptions>
                    <el-descriptions-item :label="t('common.prop.fileName')" span="3">{{ props.row.filename
                        }}</el-descriptions-item>
                    <el-descriptions-item :label="t('common.prop.identifier')" span="3">{{ props.row.form.identifier }}</el-descriptions-item>
                </el-descriptions>
            </template>
        </el-table-column>
        <el-table-column prop="stat.level" :label="t('common.prop.level')" sortable>
            <template #default="props">
                {{ t('common.level.' + props.row.stat.level) }}
            </template>
        </el-table-column>
        <el-table-column prop="stat.timems" :label="t('common.prop.time')" sortable></el-table-column>
        <el-table-column prop="stat.bv" label="3BV" sortable></el-table-column>
        <el-table-column prop="stat.bvs" label="3BV/s"
            :formatter="(row: any, column: any, cellValue: any, index: number) => { return to_fixed_n(cellValue, 3) }"
            sortable></el-table-column>
        <el-table-column :label="t('common.prop.status')" sortable sort-by="status">
            <template #default="props">
                {{ t('profile.upload.error.' + props.row.status) }}
            </template>
        </el-table-column>
        <el-table-column :label="t('common.prop.action')" :width="130">
            <template #default="props">
                <el-button :disabled="!(['pass', 'identifier', 'needApprove'].includes(props.row.status))"
                    @click="forceUpload(props.$index)"
                    :type="['pass', 'identifier'].includes(props.row.status) ? 'success' : props.row.status == 'needApprove' ? 'warning' : 'info'"
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
import type { UploadInstance, UploadProps, UploadUserFile, UploadRawFile, UploadFile, UploadFiles } from 'element-plus'
import { store } from '../store'
import { ms_to_s, to_fixed_n } from "@/utils"
import { extract_stat, get_upload_status, load_video_file, upload_form, UploadVideoForm, VideoStat } from '@/utils/fileIO';
import { Dict2FormData } from '@/utils/forms';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

interface UploadEntry {
    index: number,
    filename: string,
    status: string,
    form: UploadVideoForm | null, // for upload
    stat: VideoStat | null, // for display
}

const data = defineProps({
    identifiers: { type: Array, default: () => [] }
})

const upload_queue = ref<UploadEntry[]>([])

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
        for (let i = 0; i < upload_queue.value.length; i++) {
            upload_queue.value[i].index = i;
        }
    }

}

// 新增一条等待上传的录像信息的记录
const push_video_msg = async (uploadFile: UploadFile | UploadRawFile) => {
    let video_file;
    if ("raw" in uploadFile) {
        video_file = uploadFile.raw as UploadRawFile;
    } else {
        video_file = uploadFile as UploadRawFile;
    }
    upload_queue.value.push(await upload_prepare(video_file));
}

// 清空待上传列表
const cancel_all = () => {
    upload.value!.clearFiles();
    while (upload_queue.value.length > 0) {
        upload_queue.value.pop();
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
        if (i >= upload_queue.value.length) break;
        if (["pass", "identifier"].includes(upload_queue.value[i].status)) {
            if (upload_queue.value[i].status == "identifier") {
                store.new_identifier = true;
            }
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
    let video = upload_queue.value[i];
    if (video.status != "pass" && video.status != "identifier") {
        return;
    }
    upload_queue.value[i].status = "process";
    await getDelay();
    if (video.stat == null) {
        upload_queue.value[i].status = "upload";
        return;
    }
    await proxy.$axios.post('/video/upload/',
        Dict2FormData(video.form!),
    ).then(function (response) {
        if (response.data.type === 'success') {
            uploaded_file_num.value += 1;
            removeUpload(i);
        } else if (response.data.type === 'error' && response.data.object === 'videomodel') {
            upload_queue.value[i].status = "collision"
        } else if (response.data.type === 'error' && response.data.object === 'identifier') {
            upload_queue.value[i].status = "censorship"
        } else {
            // 正常使用不会到这里
            upload_queue.value[i].status = "upload";
        }
    }).catch((error: any) => {
        upload_queue.value[i].status = "upload";
    })
}

//删除录像
const removeUpload = (i: number) => {
    upload_queue.value.splice(i, 1);
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

async function upload_prepare(file: UploadRawFile): Promise<UploadEntry> {
    let file_u8 = new Uint8Array(await file.arrayBuffer());
    let video = load_video_file(file_u8, file.name);
    return {
        index: 0,
        filename: file.name,
        status: get_upload_status(file, video, store.user.identifiers),
        stat: extract_stat(video),
        form: upload_form(file, video),
    }
}

</script>
