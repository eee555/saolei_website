<template>
    <el-upload ref="upload" class="upload-demo" drag action="#" :limit="1" :http-request="handleVideoUpload"
        :on-exceed="handleExceed" :on-change="handleChange" :auto-upload="false" :show-file-list="false"
        style="background-color: white;">
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
                    <div class="grid-content ep-bg-purple">难度：中级</div>
                </el-col>
                <el-col :span="12">
                    <div class="grid-content ep-bg-purple">时间：23.256s</div>
                </el-col>
            </el-row>
            <el-row :gutter="5">
                <el-col :span="12">
                    <div class="grid-content ep-bg-purple">3BV：125</div>
                </el-col>
                <el-col :span="12">
                    <div class="grid-content ep-bg-purple">3BV/s：2.257</div>
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

const upload = ref<UploadInstance>()
const hint_text = ref<string>("*仅限一个文件，且文件大小不能超过5M")

const handleChange: UploadProps['onChange'] = (uploadFile: UploadFile, uploadFiles: UploadFiles) => {
    // console.log(uploadFile);
    if (uploadFile.raw?.type !== 'image/jpeg') {
        ElMessage.error('录像必须为.avf或.evf格式!')
        return false
    } else if (uploadFile.size as number / 1024 / 1024 > 5) {
        ElMessage.error('录像大小不能超过5MB!')
        return false
    }
    upload_video_visibile.value = true;
    hint_text.value = uploadFile.name;
    return true
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
    for (let i = 0;i<1;i++){
    let params = new FormData();
    params.append('file', options.file);
    params.append("software", ["e", "a"][Math.floor(Math.random() * 2)]);
    params.append("level", ["e", "i", "b"][Math.floor(Math.random() * 3)]);
    params.append("mode", "00");
    // params.append("mode", ["00", "01", "04", "05", "06", "07", "08", "09", "10", "11", "12"][Math.floor(Math.random() * 11)]);
    params.append("rtime", "523.145");
    params.append("bv", Math.ceil(Math.random() * 250).toString());
    params.append("bvs", (Math.random() * 12).toString());

    params.append("designator", "zhangsan");
    params.append("left", "111");
    params.append("right", "22");
    params.append("double", "33");
    params.append("cl", "235");
    params.append("left_s", "3.145");
    params.append("right_s", "2.055");
    params.append("double_s", "3.042");
    params.append("cl_s", "10.124");
    params.append("path", (Math.random() * 8000).toString());
    params.append("flag", "80");
    params.append("flag_s", "5.244");
    params.append("stnb", (Math.random() * 1200).toString());
    params.append("rqp", "5.244");
    params.append("ioe", (Math.random()).toString());
    params.append("thrp", "1.253");
    params.append("corr", "0.753");
    params.append("ce", "235");
    params.append("ce_s", "1.532");
    params.append("op", Math.ceil(Math.random() * 20).toString());
    params.append("isl", Math.ceil(Math.random() * 20).toString());
    params.append("cell0", Math.ceil(Math.random() * 120).toString());
    params.append("cell1", Math.ceil(Math.random() * 200).toString());
    params.append("cell2", Math.ceil(Math.random() * 150).toString());
    params.append("cell3", Math.ceil(Math.random() * 100).toString());
    params.append("cell4", Math.ceil(Math.random() * 80).toString());
    params.append("cell5", Math.ceil(Math.random() * 50).toString());
    params.append("cell6", Math.ceil(Math.random() * 30).toString());
    params.append("cell7", Math.ceil(Math.random() * 20).toString());
    params.append("cell8", Math.ceil(Math.random() * 10).toString());



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
            ElMessage.error("上传失败！小型网站，请勿攻击！")
        }
    })
}
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









