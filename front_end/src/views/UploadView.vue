<template>
    <el-upload ref="upload" class="upload-demo" drag action="#" :limit="1" :http-request="handleVideoUpload"
        :on-exceed="handleExceed" :on-change="handleChange" :auto-upload="false" :show-file-list="false"
        style="background-color: white;" accept=".avf,.evf">
        <!-- <template #trigger>
      <el-button type="primary">选择录像</el-button>
    </template> -->

        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text" style="font-size: 18px;">
            将录像拉到此处或 <em>点击此处上传</em>
        </div>

        <template #tip>
            <div class="el-upload__tip text-red" style="background-color: white;font-size: 20px;text-align: center;">

                {{ hint_text }}
            </div>
        </template>
    </el-upload>
    <div v-show="upload_video_visibile" class="upload_video">
        <img src="../assets/img/img_arbiter.png"
            style="height: 54px;width: 54px;vertical-align:middle;margin-right: 36px;" />
        <div style="display: inline-block;vertical-align:middle;width: 360px;text-align:left;">
            <el-row :gutter="5">
                <el-col :span="12">
                    <div class="grid-content ep-bg-purple">难度：{{ video_msg_level }}</div>
                </el-col>
                <el-col :span="12">
                    <div class="grid-content ep-bg-purple">时间：{{ video_msg_time }}s</div>
                </el-col>
            </el-row>
            <el-row :gutter="5">
                <el-col :span="12">
                    <div class="grid-content ep-bg-purple">3BV：{{ video_msg_bbbv }}</div>
                </el-col>
                <el-col :span="12">
                    <div class="grid-content ep-bg-purple">3BV/s：{{ video_msg_bvs }}</div>
                </el-col>
            </el-row>
        </div>
        <div style="display: inline-block;vertical-align:middle;">
            <el-button class="ml-3" type="success" @click="submitUpload"
                style="height: 60px;width: 112px;font-size: 28px;background-color: #00A2E8;border: 0;border-radius: 8px;">
                上传
            </el-button>
        </div>
    </div>
</template>
  
<script lang="ts" setup>
// 上传录像的页面
import { onMounted, ref, Ref, defineEmits } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
import { genFileId, ElMessage } from 'element-plus'
import type { UploadInstance, UploadProps, UploadRawFile, UploadFile, UploadFiles, UploadRequestOptions } from 'element-plus'
// import img_arbiter from '@/assets/img/img_arbiter.png'

const video_msg_level = ref("")
const video_msg_time = ref("")
const video_msg_bbbv = ref("")
const video_msg_bvs = ref("")

const upload = ref<UploadInstance>()
const hint_text = ref<string>("*仅限一个文件，且文件大小不能超过5M")

const handleChange: UploadProps['onChange'] = (uploadFile: UploadFile, uploadFiles: UploadFiles) => {
    // console.log(uploadFile);
    if (uploadFile.raw?.type == 'image/jpeg') {
        // el-upload在限制，进不来
        ElMessage.error('不能上传图片!')
        return false
    } else if (uploadFile.size as number / 1024 / 1024 > 5) {
        ElMessage.error('录像大小不能超过5MB!')
        return false
    }
    upload_video_visibile.value = true;
    hint_text.value = uploadFile.name;
    modify_video_msg(uploadFile);
    return true
}

const modify_video_msg = async (uploadFile: UploadFile) => {
    const ms = await import("ms-toollib");
    let video_file = await uploadFile.raw!.arrayBuffer();
    let video_file_u8 = new Uint8Array(video_file);
    let aa = ms.AvfVideo.new(video_file_u8, uploadFile.name);
    aa.parse_video();
    aa.analyse();
    aa.current_time = 1e8;  //时间设置到最后（超出就是最后）
    video_msg_level.value = ["初级", "中级", "高级"][aa.get_level - 3];
    video_msg_time.value = aa.get_rtime.toFixed(3);
    video_msg_bbbv.value = aa.get_bbbv + "";
    video_msg_bvs.value = aa.get_bbbv_s.toFixed(3);
}

const handleExceed: UploadProps['onExceed'] = (files) => {
    upload.value!.clearFiles()
    const file = files[0] as UploadRawFile
    file.uid = genFileId()
    upload.value!.handleStart(file)
}

// // 限制录像格式和大小
// const beforeUpload: UploadProps['beforeUpload'] = (rawFile) => {
//     console.log(666);

//   if (rawFile.type !== 'image/jpeg') {
//     console.log(777);
//     ElMessage.error('Video must be AVF or EVF format!')
//     return false
//   } else if (rawFile.size / 1024 / 1024 > 5) {
//     ElMessage.error('Video size can not exceed 5MB!')
//     return false
//   }
//   return true
// }

const submitUpload = () => {
    // console.log(document.cookie);
    upload.value!.submit()
}


const handleVideoUpload = async (options: UploadRequestOptions) => {
    const ms = await import("ms-toollib");
    // console.log(options.file);
    let video_file = options.file;
    let video_file_u8 = new Uint8Array(await video_file.arrayBuffer());
    let aa = ms.AvfVideo.new(video_file_u8, video_file.name);
    aa.parse_video();
    aa.analyse();
    aa.current_time = 1e8;  //时间设置到最后（超出就是最后）
    if (aa.get_level > 5) {
        ElMessage.error('不能上传自定义的录像!')
        return
    }
    if (video_file.name.slice(-3) != "avf" && video_file.name.slice(-3) != "evf") {
        ElMessage.error('录像必须为.avf或.evf格式!')
        return
    }
    if (video_file.name.length >= 100) {
        ElMessage.error('录像文件名太长!')
        return
    }
    if (!aa.get_is_completed) {
        ElMessage.error('没有扫开的录像!')
        return
    }

    const decoder = new TextDecoder();
    // for (let i = 0;i<1;i++){

    // console.log(aa.get_level);

    let params = new FormData();
    params.append('file', options.file);
    params.append("software", ["e", "a"][video_file.name.slice(-3) == "avf" ? 1 : 0]);
    params.append("level", ["b", "i", "e"][aa.get_level - 3]);
    params.append("mode", String(aa.get_mode).padStart(2, '0'));
    params.append("rtime", aa.get_rtime.toFixed(3));
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
            upload.value!.clearFiles()
            upload_video_visibile.value = false;
            ElMessage.success("上传成功！")
            hint_text.value = "*仅限一个文件，且文件大小不能超过5M"
        } else if (response.data.status >= 101) {
            // 正常使用不会到这里
            ElMessage.error("上传失败！小型网站，请勿攻击！");
            upload.value!.clearFiles();
        }
    })
    // }
}




const upload_video_visibile = ref(false)
// const register_visibile = ref(false)





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

/* .el-col {
    border-radius: 4px;
}

.grid-content {
    border-radius: 4px;
    min-height: 36px;
} */
</style>









