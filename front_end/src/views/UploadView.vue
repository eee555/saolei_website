<template>
    <el-upload
        ref="upload" v-model:file-list="fileList" :disabled="store.user.realname == '匿名'" drag action="#"
        :multiple="true" :on-change="handleChange" :auto-upload="false" :show-file-list="false"
        accept=".avf,.evf,.rmv,.mvf"
    >
        <el-icon class="el-icon--upload">
            <upload-filled />
        </el-icon>
        <div
            class="el-upload__text" style="font-size: 18px;"
        >
            <span v-if="store.user.realname == '匿名'">
                {{ t('common.msg.realNameRequired') }}
            </span>
            <span v-else>
                {{ t('profile.upload.dragOrClick1') }}
                <em>
                    {{ t('profile.upload.dragOrClick2') }}
                </em>
            </span>
        </div>

        <template #tip>
            <div style="text-align: center;">
                <el-button
                    v-show="upload_queue.length > 0" size="large" type="primary"
                    style="display: block;margin: 16px auto;font-size: 18px;width: 220px;" @click="submitUpload()"
                >
                    {{ t('profile.upload.uploadAll', [upload_queue.length]) }}
                </el-button>
                <el-button
                    v-show="upload_queue.length > 0" size="small" type="info"
                    style="display: block;margin: 16px auto;width: 120px;" @click="cancel_all()"
                >
                    {{ t('profile.upload.cancelAll') }}
                </el-button>
                <span style="font-size: 14px;">{{ t('profile.upload.constraintNote') }}</span>
            </div>
        </template>
    </el-upload>
    <el-table :data="upload_queue" table-layout="auto">
        <el-table-column type="expand">
            <template #default="props">
                <el-descriptions>
                    <el-descriptions-item :label="t('common.prop.fileName')" :span="3">
                        {{ props.row.filename }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.prop.cl')">
                        {{ props.row.stat.displayStat('cl') }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.prop.ce')" :span="2">
                        {{ props.row.stat.displayStat('ce') }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.prop.cl_s')">
                        {{ props.row.stat.displayStat('cls') }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.prop.ce_s')" :span="2">
                        {{ props.row.stat.displayStat('ces') }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.prop.ioe')">
                        {{ props.row.stat.displayStat('ioe') }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.prop.thrp')">
                        {{ props.row.stat.displayStat('thrp') }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('common.prop.corr')">
                        {{ props.row.stat.displayStat('corr') }}
                    </el-descriptions-item>
                </el-descriptions>
            </template>
        </el-table-column>
        <el-table-column :label="t('common.prop.status')" sortable sort-by="status">
            <template #default="{ row }">
                {{ t(`profile.upload.error.${row.status}`) }}
            </template>
        </el-table-column>
        <el-table-column prop="stat.end_time" :label="t('common.prop.end_time')" :width="150">
            <template #default="{ row }">
                {{ row.stat ? toISODateTimeString(row.stat.end_time) : '' }}
            </template>
        </el-table-column>
        <el-table-column prop="stat.level" :label="t('common.prop.level')" sortable>
            <template #default="{ row }">
                {{ row.stat ? t(`common.level.${row.stat.level}`) : '' }}
            </template>
        </el-table-column>
        <el-table-column prop="stat.timems" :label="t('common.prop.time')" sortable>
            <template #default="{ row }">
                {{ row.stat ? row.stat.displayStat('time') : '' }}
            </template>
        </el-table-column>
        <el-table-column prop="stat.bv" :label="t('common.prop.bv')" sortable />
        <el-table-column :label="t('common.prop.bvs')" sortable :sort-by="(v) => v.bvs()">
            <template #default="{ row }">
                {{ row.stat ? row.stat.displayStat('bvs') : '' }}
            </template>
        </el-table-column>
        <el-table-column :label="t('common.prop.action')" :width="130">
            <template #default="props">
                <el-button
                    :disabled="!(['pass', 'identifier', 'needApprove'].includes(props.row.status))"
                    :type="['pass', 'identifier'].includes(props.row.status) ? 'success' : props.row.status == 'needApprove' ? 'warning' : 'info'"
                    circle @click="forceUpload(props.$index)"
                >
                    <base-icon-upload />
                </el-button>
                <el-button type="danger" circle @click="removeUpload(props.$index)">
                    <base-icon-delete />
                </el-button>
            </template>
        </el-table-column>
    </el-table>
</template>

<script lang="ts" setup>
// 上传录像的页面
import { ref } from 'vue';
import { ElTable, ElTableColumn, ElButton, ElDescriptions, ElDescriptionsItem, ElUpload, ElIcon } from 'element-plus';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
const { proxy } = useCurrentInstance();
import type { UploadInstance, UploadProps, UploadUserFile, UploadRawFile, UploadFile, UploadFiles } from 'element-plus';
import { store } from '../store';
import { extract_stat, get_upload_status, load_video_file, upload_form, UploadVideoForm } from '@/utils/fileIO';
import { Dict2FormData } from '@/utils/forms';
import { useI18n } from 'vue-i18n';
import BaseIconDelete from '@/components/common/BaseIconDelete.vue';
import BaseIconUpload from '@/components/common/BaseIconUpload.vue';
import { VideoAbstract } from '@/utils/videoabstract';
import { toISODateTimeString } from '@/utils/datetime';

const { t } = useI18n();

interface UploadEntry {
    index: number;
    filename: string;
    status: string;
    form: UploadVideoForm | null; // for upload
    stat: VideoAbstract | null; // for display
}

defineProps({
    identifiers: { type: Array, default: () => [] },
});

const upload_queue = ref<UploadEntry[]>([]);

const fileList = ref<UploadUserFile[]>([]);

const upload = ref<UploadInstance>();
const uploaded_file_num = ref<number>(0);
const allow_upload = ref(true);

// 录像列表变动的回调，上传多个文件时，有几个文件就会进来几次。
const handleChange: UploadProps['onChange'] = async (uploadFile: UploadFile, _uploadFiles: UploadFiles) => {
    if (allow_upload.value) {
        // upload_video_visible.value = true;
        await push_video_msg(uploadFile);
        // 修改id。最后一个协程才是真正起作用的。
        for (let i = 0; i < upload_queue.value.length; i++) {
            upload_queue.value[i].index = i;
        }
    }
};

// 新增一条等待上传的录像信息的记录
const push_video_msg = async (uploadFile: UploadFile | UploadRawFile) => {
    let video_file;
    if ('raw' in uploadFile) {
        video_file = uploadFile.raw as UploadRawFile;
    } else {
        video_file = uploadFile as UploadRawFile;
    }
    upload_queue.value.push(await upload_prepare(video_file));
};

// 清空待上传列表
const cancel_all = () => {
    upload.value!.clearFiles();
    while (upload_queue.value.length > 0) {
        upload_queue.value.pop();
    }
    uploaded_file_num.value = 0;
};

// 点上传按钮的回调，自动上传录像
const submitUpload = async () => {
    // 先锁死，不让进变化回调
    allow_upload.value = false;
    let i = 0;
    let count = 0; // 最多上传99个
    while (count < 99) {
        if (i >= upload_queue.value.length) break;
        if (['pass', 'identifier'].includes(upload_queue.value[i].status)) {
            if (upload_queue.value[i].status == 'identifier') {
                store.new_identifier = true;
            }
            await forceUpload(i);
            count++;
            continue;
        }
        i++;
    }
    allow_upload.value = true;
};

// 上传问题不大的录像
const forceUpload = async (i: number) => {
    const video = upload_queue.value[i];
    if (video.status != 'pass' && video.status != 'identifier') {
        return;
    }
    upload_queue.value[i].status = 'process';
    await getDelay();
    if (video.stat == null) {
        upload_queue.value[i].status = 'upload';
        return;
    }
    await proxy.$axios.post('/common/uploadvideo/',
        Dict2FormData(video.form!),
    ).then(function (response) {
        if (response.data.type === 'success') {
            uploaded_file_num.value += 1;
            upload_queue.value[i].stat!.id = response.data.data.id;
            upload_queue.value[i].stat!.state = response.data.data.state;
            store.user.videos.push(upload_queue.value[i].stat!);
            if (store.user.id === store.player.id) {
                store.player.videos.push(upload_queue.value[i].stat!);
            }
            removeUpload(i);
        } else if (response.data.type === 'error' && response.data.object === 'videomodel') {
            upload_queue.value[i].status = 'collision';
        } else if (response.data.type === 'error' && response.data.object === 'identifier') {
            upload_queue.value[i].status = 'censorship';
        } else {
            // 正常使用不会到这里
            upload_queue.value[i].status = 'upload';
        }
    }).catch((_error: any) => {
        upload_queue.value[i].status = 'upload';
    });
};

// 删除录像
const removeUpload = (i: number) => {
    upload_queue.value.splice(i, 1);
};

// 均匀延时，降低并发。
function getDelay() {
    return new Promise((resolve) => {
        const delay = 200;
        setTimeout(() => {
            resolve(delay);
        }, delay);
    });
}

async function upload_prepare(file: UploadRawFile): Promise<UploadEntry> {
    const file_u8 = new Uint8Array(await file.arrayBuffer());
    try {
        const video = load_video_file(file_u8, file.name);
        return {
            index: 0,
            filename: file.name,
            status: get_upload_status(file, video, store.user.identifiers),
            stat: extract_stat(video),
            form: upload_form(file, video),
        };
    } catch (_e) {
        return {
            index: 0,
            filename: file.name,
            status: 'parse',
            stat: null,
            form: null,
        };
    }
}

</script>
