<template>
    <el-upload v-model:file-list="fileList" :disabled="!allow_upload" ref="upload" drag action="#" :limit="99"
        :multiple="true" :http-request="handleVideoUpload" :on-exceed="handleExceed" :on-change="handleChange"
        :auto-upload="false" :show-file-list="false" style="background-color: white;" accept=".avf,.evf">
        <!-- <template #trigger>
      <el-button type="primary">选择录像</el-button>
    </template> -->

        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text" style="font-size: 18px;">
            将录像拉到此处或 <em>点击此处选择</em>
        </div>

        <template #tip>

            <div class="el-upload__tip text-red" style="background-color: white;text-align: center;">
                <el-button @click="submitUpload()" size="large" type="primary" v-show="video_msgs.length > 0"
                    style="display: block;margin: 16px auto;font-size: 18px;width: 220px;">一键上传（{{ video_msgs.length
                    }}个）</el-button>
                <el-button @click="cancel_all()" size="small" type="info" v-show="video_msgs.length > 0"
                    style="display: block;margin: 16px auto;width: 120px;" plain>全部清空</el-button>
                <span style="font-size: 14px;">*单个文件大小不能超过5M，文件数量不能超过99</span>
            </div>
        </template>
    </el-upload>
    <div style="width:496px; margin: 0 auto;">
        <transition-group name="card_fade">
            <UploadVideoCard v-for="(video_msg, index) in video_msgs" @cancel_this="cancel_video_id"
                :video_msg="video_msg" :key="video_msg.filename">
            </UploadVideoCard>
        </transition-group>
    </div>
</template>

<script lang="ts" setup>
// 上传录像的页面
import { onMounted, onUnmounted, ref } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
import { genFileId, ElMessage, MessageHandler } from 'element-plus'
import type { UploadInstance, UploadProps, UploadUserFile, UploadRawFile, UploadFile, UploadFiles, UploadRequestOptions } from 'element-plus'
// import img_arbiter from '@/assets/img/img_arbiter.png'
import UploadVideoCard from '@/components/UploadVideoCard.vue';
import store from '../store'

const video_msgs = ref<{
    uid: number,
    id: number,
    filename: string,
    level: string,
    timems: string,
    bbbv: string,
    bvs: string,
}[]>([])

const fileList = ref<UploadUserFile[]>([])

const upload = ref<UploadInstance>();
const uploaded_file_num = ref<number>(0);
const allow_upload = ref(true)

// 延时系数
let k = 0;

// 切标签时msg关不掉
const elmsg_handles: MessageHandler[] = [];

onMounted(() => {
    const player = store.state.user;
    if (player.realname == "请修改为实名") {
        allow_upload.value = false;
        elmsg_handles.push(ElMessage.error({ message: '上传录像前，请先修改为实名!', offset: 68 }));
    }
    if (!player.realname) {
        allow_upload.value = false;
        elmsg_handles.push(ElMessage.error({ message: '请先登录!', offset: 68 }));
    }

})

onUnmounted(() => {
    elmsg_handles.forEach((h) => { h.close() });
})

// 录像列表变动的回调，上传多个文件时，有几个文件就会进来几次。
const handleChange: UploadProps['onChange'] = async (uploadFile: UploadFile, uploadFiles: UploadFiles) => {

    if (allow_upload.value) {
        if (uploadFile.raw?.type == 'image/jpeg') {
            // el-upload在限制，进不来。除非用户选全部文件。
            elmsg_handles.push(ElMessage.error({ message: '不能上传图片!', offset: 68 }));

        } else if (uploadFile.size as number / 1024 / 1024 > 5) {
            elmsg_handles.push(ElMessage.error({ message: '录像大小不能超过5MB!', offset: 68 }));

        }
        // upload_video_visibile.value = true;
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
    let video_file;
    if ("raw" in uploadFile) {
        video_file = await uploadFile.raw!.arrayBuffer();
    } else {
        video_file = await (uploadFile as UploadRawFile).arrayBuffer();
    }
    let video_file_u8 = new Uint8Array(video_file);
    let aa;
    if (uploadFile.name.slice(-3) == "avf") {
        aa = ms.AvfVideo.new(video_file_u8, uploadFile.name);
    } else if (uploadFile.name.slice(-3) == "evf") {
        aa = ms.EvfVideo.new(video_file_u8, uploadFile.name);
    } else {
        elmsg_handles.push(ElMessage.error({ message: '录像文件的后缀不正确!', offset: 68 }));
        return
    }
    aa.parse_video();
    aa.analyse();
    aa.current_time = 1e8;  //时间设置到最后（超出就是最后）
    video_msgs.value.push({
        uid: uploadFile.uid,
        id: 0,
        filename: uploadFile.name,
        level: ["初级", "中级", "高级"][aa.get_level - 3],
        timems: aa.get_rtime_ms + "",
        bbbv: aa.get_bbbv + "",
        bvs: aa.get_bbbv_s.toFixed(3),
    })
}

const handleExceed: UploadProps['onExceed'] = async (files) => {
    elmsg_handles.push(ElMessage.error({ message: '单次最多上传99个录像！', offset: 68 }));
    const left_num = 99 - video_msgs.value.length;
    files.splice(left_num);

    for (let file of files) {
        const f = file as UploadRawFile;
        f.uid = genFileId();
        allow_upload.value = false; // 暂时屏蔽onChange回调
        upload.value!.handleStart(f);
        allow_upload.value = true;
        await push_video_msg(f);
        // 修改id。最后一个协程才是真正起作用的。
        for (let i = 0; i < video_msgs.value.length; i++) {
            video_msgs.value[i].id = i;
        }
    }

}

// 点录像信息卡片右侧叉的回调
const cancel_video_id = (id: number) => {
    delete_from_file_list(video_msgs.value[id].uid);
    video_msgs.value.splice(id, 1);
    for (let i = 0; i < video_msgs.value.length; i++) {
        video_msgs.value[i].id = i;
    }
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

// 用uid做匹配，在fileList中删除对应的待上传录像。不能简单地按照id来删。两个array里顺序不同。
const delete_from_file_list = (uid: number) => {
    fileList.value = fileList.value.filter((x) => x.uid != uid);
}

// 点上传按钮的回调
const submitUpload = () => {
    // 先锁死，不让进变化回调
    allow_upload.value = false;
    upload.value!.submit()
}

// 均匀延时，降低并发。
function getDelay() {
    return new Promise(resolve => {
        const delay = k * 200;
        k++;
        setTimeout(() => {
            resolve(delay);
        }, delay);
    });
}


function cancel_all_or_not() {
    uploaded_file_num.value += 1;
    if (uploaded_file_num.value == video_msgs.value.length) {
        cancel_all();
        allow_upload.value = true;
    }
}


// 上传几个录像就进来几次
const handleVideoUpload = async (options: UploadRequestOptions) => {
    await getDelay();
    const ms = await import("ms-toollib");
    let video_file = options.file;
    let video_file_u8 = new Uint8Array(await video_file.arrayBuffer());
    // let aa = ms.AvfVideo.new(video_file_u8, video_file.name);
    let aa;
    if (video_file.name.slice(-3) == "avf") {
        aa = ms.AvfVideo.new(video_file_u8, video_file.name);
    } else if (video_file.name.slice(-3) == "evf") {
        aa = ms.EvfVideo.new(video_file_u8, video_file.name);
    } else {
        elmsg_handles.push(ElMessage.error({ message: '录像文件的后缀不正确！', offset: 68 }));
        return
    }
    aa.parse_video();
    aa.analyse();
    aa.current_time = 1e8;  //时间设置到最后（超出就是最后）
    if (aa.get_level > 5) {
        elmsg_handles.push(ElMessage.error({ message: '不能上传自定义的录像！', offset: 68 }));
        cancel_all_or_not();
        return
    }
    if (video_file.name.slice(-3) != "avf" && video_file.name.slice(-3) != "evf") {
        elmsg_handles.push(ElMessage.error({ message: '录像必须为.avf或.evf格式！', offset: 68 }));
        cancel_all_or_not();
        return
    }
    if (video_file.name.length >= 100) {
        elmsg_handles.push(ElMessage.error({ message: '录像文件名太长！', offset: 68 }));

        cancel_all_or_not();
        return
    }
    if (!aa.get_is_completed) {
        elmsg_handles.push(ElMessage.error({ message: '没有扫开的录像！', offset: 68 }));
        cancel_all_or_not();
        return
    }
    // console.log(aa.is_valid());

    if (aa.is_valid() == 1) {
        elmsg_handles.push(ElMessage.error({ message: '非法的录像！', offset: 68 }));
        cancel_all_or_not();
        return
    }

    const decoder = new TextDecoder();

    let params = new FormData();
    params.append('file', options.file);
    params.append('review_code', aa.is_valid() + "");
    params.append("software", ["e", "a"][video_file.name.slice(-3) == "avf" ? 1 : 0]);
    params.append("level", ["b", "i", "e"][aa.get_level - 3]);
    params.append("mode", String(aa.get_mode).padStart(2, '0'));
    params.append("timems", aa.get_rtime_ms + "");
    params.append("bv", aa.get_bbbv + "");
    params.append("bvs", aa.get_bbbv_s + "");
    params.append("designator", decoder.decode(aa.get_player_designator));
    params.append("left", aa.get_left + "");
    params.append("right", aa.get_right + "");
    params.append("double", aa.get_double + "");
    params.append("cl", aa.get_cl + "");
    params.append("left_s", aa.get_left_s + "");
    params.append("right_s", aa.get_right_s + "");
    params.append("double_s", aa.get_double_s + "");
    params.append("cl_s", aa.get_cl_s + "");
    params.append("path", aa.get_path + "");
    params.append("flag", aa.get_flag + "");
    params.append("flag_s", aa.get_flag_s + "");
    params.append("stnb", aa.get_stnb + "");
    params.append("rqp", aa.get_rqp + "");
    params.append("ioe", aa.get_ioe + "");
    params.append("thrp", aa.get_thrp + "");
    params.append("corr", aa.get_corr + "");
    params.append("ce", aa.get_ce + "");
    params.append("ce_s", aa.get_ce_s + "");
    params.append("op", aa.get_op + "");
    params.append("isl", aa.get_isl + "");
    params.append("cell0", aa.get_cell0 + "");
    params.append("cell1", aa.get_cell1 + "");
    params.append("cell2", aa.get_cell2 + "");
    params.append("cell3", aa.get_cell3 + "");
    params.append("cell4", aa.get_cell4 + "");
    params.append("cell5", aa.get_cell5 + "");
    params.append("cell6", aa.get_cell6 + "");
    params.append("cell7", aa.get_cell7 + "");
    params.append("cell8", aa.get_cell8 + "");

    proxy.$axios.post('/video/upload/',
        params,
    ).then(function (response) {
        if (response.data.status == 100) {
            // upload.value!.clearFiles()
            // upload_video_visibile.value = false;
            elmsg_handles.push(ElMessage.success({
                message: `上传成功！剩余（${video_msgs.value.length - uploaded_file_num.value - 1}）`,
                offset: 68
            }));

            // hint_text.value = "*仅限一个文件，且文件大小不能超过5M"
            uploaded_file_num.value += 1;

            if (uploaded_file_num.value == video_msgs.value.length) {
                cancel_all();
                allow_upload.value = true;
            }
        } else if (response.data.status >= 101) {
            // 正常使用不会到这里
            // elmsg_handles.push(ElMessage.error({ message: '上传失败！小型网站，请勿攻击！', offset: 68 }));
            cancel_all_or_not();
        }
    }).catch(() => {
        elmsg_handles.push(ElMessage.error({ message: '上传失败！服务器无响应！', offset: 68 }));
        cancel_all_or_not();
    })
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
