<template>
    <div class="common-layout">
        <el-container>
            <el-aside width="30%">
                <div v-if="is_editing">
                    <el-upload ref="upload" class="avatar-uploader" action="#" :limit="1" :show-file-list="false"
                        :auto-upload="false" :on-exceed="handleExceed" :on-change="handleChange"
                        :before-upload="beforeAvatarUpload" :http-request="handleAvatarUpload"
                        style="width: 200px; height: 300px">
                        <el-image style="width: 200px; height: 300px" v-if="imageUrl" :src="imageUrl" :fit="'cover'" />
                        <el-icon v-else class="avatar-uploader-icon">
                            <Plus />
                        </el-icon>
                    </el-upload>
                    <div style="font-size: 14px;color: #AAA;text-align: center;">*点击图片修改头像</div>
                    <el-row :gutter="0">
                        <el-col :span="5" style="margin-top: 16px;">
                            <div>
                                <strong>姓名：</strong>
                            </div>
                        </el-col>
                        <el-col :span="19" style="margin-top: 16px;">
                            <div>
                                <el-input v-model="realname_edit" placeholder="请输入真实姓名" minlength="2" maxlength="10"></el-input>
                            </div>
                        </el-col>
                    </el-row>
                    <el-row :gutter="0">
                        <el-col :span="5" style="margin-top: 16px;">
                            <div>
                                <strong>个性签名：</strong>
                            </div>
                        </el-col>
                        <el-col :span="19" style="margin-top: 16px;">
                            <div>
                                <el-input v-model="signature_edit" placeholder="请输入个性签名" minlength="0"
                                    maxlength="188"></el-input>
                            </div>
                        </el-col>
                    </el-row>
                    <el-button type="success" :plain="false" :size="'large'" @click="upload_info"
                        style="font-size: 18px;margin-top: 18px;width: 120px;">确认</el-button>
                    <el-button type="success" :plain="true" :size="'large'" @click="is_editing = false;"
                        style="font-size: 18px;margin-top: 18px;width: 80px;">取消</el-button>

                </div>

                <div v-else>
                    <div :key="'cover'" class="avatar-uploader">
                        <el-image style="width: 200px; height: 300px" :src="require('@/assets/person.png')"
                            :fit="'cover'" />
                    </div>
                    <div style="font-size: 30px;margin-top: 10px;margin-bottom: 8px;">{{ username }}</div>
                    <div style="font-size: 20px;margin-bottom: 8px;">{{ realname }}</div>
                    <div><strong>个性签名：</strong>{{ signature }}</div>

                    <el-button type="primary" :plain="true" :size="'large'" @click="is_editing = true;"
                        style="font-size: 18px;margin-top: 18px;width: 160px;">修改个人资料</el-button>
                </div>
            </el-aside>
            <el-main>Main</el-main>
        </el-container>
    </div>
</template>
  
<script lang="ts" setup>
// 注册、登录的弹框及右上方按钮
import { onMounted, ref, Ref, defineEmits } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
import { genFileId, ElMessage } from 'element-plus'
import type { UploadInstance, UploadProps, UploadRawFile, UploadFile, UploadFiles, UploadRequestOptions } from 'element-plus'
const upload = ref<UploadInstance>()
import { Plus } from '@element-plus/icons-vue'
const imageUrl = ref(require('@/assets/person.png'))
const is_editing = ref(false);

//编辑前的
const username = ref("");
const realname = ref("");
const signature = ref("");

//编辑状态时的
const realname_edit = ref("");
const signature_edit = ref("");

onMounted(() => {
    const player = proxy.$store.state.player;
    username.value = player.name;
    // proxy.$axios.get('/msuser/info/',
    //     {
    //         params: {
    //             id: player.id,
    //         }
    //     }
    // ).then(function (response) {
    //     const data = JSON.parse(response.data);
    //     if ((data.videos).length >= 0) {

    //         // console.log(index_tag_selected);

    //     } else {
    //         // console.log("000");
    //     }
    // })
})

const upload_info = () => {
    is_editing.value = false;
    if (imageUrl) {
        upload.value!.submit();
    } else {
        let params = new FormData()
        params.append('realname', realname.value)
        params.append('signature', signature.value)
        proxy.$axios.post('/msuser/update/',
            params,
        ).then(function (response) {
            if (response.data.status == 100) {
                ElMessage.success("信息更新成功！")
            } else if (response.data.status >= 101) {
                ElMessage.error("信息更新失败！")
            }
        })
    }
}

// 把头像、姓名、个性签名传上去
const handleAvatarUpload = async (options: UploadRequestOptions) => {
    // console.log(666);

    let params = new FormData()
    params.append('avatar', options.file);
    params.append('realname', realname_edit.value)
    params.append('signature', signature_edit.value)
    proxy.$axios.post('/msuser/update/',
        params,
    ).then(function (response) {
        if (response.data.status == 100) {
            console.log(677);
            ElMessage.success("信息更新成功！")
        } else if (response.data.status >= 101) {
            ElMessage.error((Object.values(response.data.msg)[0] as string[])[0])
        }
    })


}

const handleChange: UploadProps['onChange'] = (uploadFile: UploadFile, uploadFiles: UploadFiles) => {
    if (!uploadFile.url) {
        uploadFile.url = URL.createObjectURL(uploadFile.raw!)
    }
    imageUrl.value = uploadFile.url;
}

const handleExceed: UploadProps['onExceed'] = (files) => {
    upload.value!.clearFiles()
    const file = files[0] as UploadRawFile
    file.uid = genFileId()
    upload.value!.handleStart(file)
}

const beforeAvatarUpload: UploadProps['beforeUpload'] = (rawFile) => {
    console.log(rawFile);

    if (rawFile.type !== 'image/jpeg') {
        ElMessage.error('头像必须为JPG格式!')
        return false
    } else if (rawFile.size / 1024 / 512 * 0) {
        ElMessage.error('头像大小不能超过512kB!')
        return false
    }
    return true
}


















</script>


<style>
.avatar-uploader {
    margin: auto;
    text-align: center;
    margin-top: 30px;

}
</style>









