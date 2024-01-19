<template>
    <div class="common-layout">
        <el-container>
            <el-aside width="30%">
                <div v-if="is_editing">
                    <el-upload ref="upload" class="avatar-uploader" action="#" :limit="1" :show-file-list="false"
                        :auto-upload="false" :on-exceed="handleExceed" :on-change="handleChange"
                        :before-upload="beforeAvatarUpload" :http-request="handleAvatarUpload"
                        style="width: 200px; height: 200px;border-radius: 12px;">
                        <el-image style="width: 200px; height: 200px;border-radius: 12px;" v-if="imageUrl" :src="imageUrl"
                            :fit="'cover'" />
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
                                <el-input v-model.trim="realname_edit" placeholder="请输入真实姓名" minlength="2"
                                    maxlength="10"></el-input>
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
                                <el-input v-model.trim="signature_edit" placeholder="请输入个性签名" minlength="0"
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
                        <el-image style="width: 200px; height: 200px;border-radius: 12px;" :src="imageUrl" :fit="'cover'" />
                    </div>
                    <div style="font-size: 30px;margin-top: 10px;margin-bottom: 8px;">
                        {{ username }}
                        <span style="font-size: 18px; color: #555;">id: {{ userid }}</span>
                    </div>
                    <div style="font-size: 20px;margin-bottom: 8px;">{{ realname }}</div>
                    <div style="overflow: auto ;"><strong>个性签名：</strong>{{ signature }}</div>

                    <el-button v-show="show_edit_button" type="primary" :plain="true" :size="'large'"
                        @click="is_editing = true;"
                        style="font-size: 18px;margin-top: 18px;width: 160px;">修改个人资料</el-button>
                </div>
            </el-aside>

            <el-main>
                <el-tabs v-model="activeName" style="max-height: 1024px; overflow: auto;">
                    <el-tab-pane label="个人纪录" name="first" :lazy="true">
                        <PlayerRecordView></PlayerRecordView>
                    </el-tab-pane>
                    <el-tab-pane label="全部录像" name="second" :lazy="true">
                        <PlayerVideosView></PlayerVideosView>
                    </el-tab-pane>
                </el-tabs>

            </el-main>
        </el-container>
    </div>
</template>
  
<script lang="ts" setup>
// 注册、登录的弹框及右上方按钮
import { onMounted, ref, Ref, defineEmits, defineAsyncComponent, computed } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
// import PreviewDownload from '@/components/PreviewDownload.vue';
import PlayerRecordView from '@/views/PlayerRecordView.vue';
import PlayerVideosView from '@/views/PlayerVideosView.vue';
// const AsyncPlayerVideosView = defineAsyncComponent(() => import('@/views/PlayerVideosView.vue'));


const { proxy } = useCurrentInstance();
import { genFileId, ElMessage } from 'element-plus'
import type { UploadInstance, UploadProps, UploadRawFile, UploadFile, UploadFiles, UploadRequestOptions } from 'element-plus'
const upload = ref<UploadInstance>()
import { Plus } from '@element-plus/icons-vue'
const imageUrl = ref(require('@/assets/person.png'))
const avatar_changed = ref(false);
import { Record, RecordBIE } from "@/utils/common/structInterface";
import { compress, compressAccurately } from 'image-conversion';

const loading = ref(true)

//编辑前的
const userid = ref("");
const username = ref("");
const realname = ref("");
const signature = ref("");

//编辑状态时的
const realname_edit = ref("");
const signature_edit = ref("");

// 是否在编辑的标识
const is_editing = ref(false);

// 标签默认切在第一页
const activeName = ref('first')
// const player = proxy.$store.state.player;
const player = JSON.parse(localStorage.getItem("player") as string);
// console.log(player);

const user = proxy.$store.state.user;
const show_edit_button = player.id == user.id;

onMounted(() => {
    // 把左侧的头像、姓名、个性签名、记录请求过来
    proxy.$axios.get('/msuser/info/',
        {
            params: {
                id: player.id,
            }
        }
    ).then(function (response) {
        const data = response.data;
        userid.value = data.id;
        realname.value = data.realname;
        username.value = data.username;

        signature.value = data.signature;
        realname_edit.value = data.realname;
        signature_edit.value = data.signature;
        // console.log(imageUrl);
        if (data.avatar) {
            imageUrl.value = "data:image/;base64," + data.avatar;
        }
        // console.log(imageUrl);
        loading.value = false;

    })

    // 再把个人纪录请求过来
    // std_record
})

// 修改确认按钮的回调，改过图片就走unload的回调上传，否则就按钮本身回调上传
const upload_info = () => {
    is_editing.value = false;
    if (avatar_changed.value) {
        upload.value!.submit();
    } else {
        let params = new FormData()
        if (realname_edit.value != realname.value) {
            params.append('realname', realname_edit.value)
        }
        if (signature_edit.value != signature.value) {
            params.append('signature', signature_edit.value)
        }
        proxy.$axios.post('/msuser/update/',
            params,
        ).then(function (response) {
            if (response.data.status == 100) {
                if (realname_edit.value != realname.value) {
                    if (!response.data.msg.realname_flag) {
                        ElMessage.warning("姓名剩余修改次数不足！")
                        realname_edit.value = realname.value;
                    } else {
                        ElMessage.success(`姓名修改成功！剩余修改次数${response.data.msg.left_realname_n}`)
                        realname.value = realname_edit.value;
                    }
                }
                if (signature_edit.value != signature.value) {
                    if (!response.data.msg.signature_flag) {
                        ElMessage.warning("个性签名剩余修改次数不足！")
                        signature_edit.value = signature.value;
                    } else {
                        ElMessage.success(`个性签名修改成功！剩余修改次数${response.data.msg.left_signature_n}`)
                        signature.value = signature_edit.value;
                    }
                }
                proxy.$store.commit('updateUser', response.data.msg);// 当前登录用户
                // proxy.$store.commit('updatePlayer', response.data.msg);// 看我的地盘看谁的
                localStorage.setItem("player", JSON.stringify(response.data.msg));

            } else if (response.data.status >= 101) {
                ElMessage.error(response.data.msg)
            }
        })

    }



}

// 把头像、姓名、个性签名传上去
const handleAvatarUpload = async (options: UploadRequestOptions) => {
    let params = new FormData()
    params.append('avatar', options.file);
    params.append('realname', realname_edit.value)
    params.append('signature', signature_edit.value)
    proxy.$axios.post('/msuser/update/',
        params,
    ).then(function (response) {
        if (response.data.status == 100) {
            if (realname_edit.value != realname.value) {
                if (!response.data.msg.realname_flag) {
                    ElMessage.warning("姓名剩余修改次数不足！")
                    realname_edit.value = realname.value;
                } else {
                    ElMessage.success(`姓名修改成功！剩余修改次数${response.data.msg.left_realname_n}`)
                    realname.value = realname_edit.value;
                }
            }
            if (signature_edit.value != signature.value) {
                if (!response.data.msg.signature_flag) {
                    ElMessage.warning("个性签名剩余修改次数不足！")
                    signature_edit.value = signature.value;
                } else {
                    ElMessage.success(`个性签名修改成功！剩余修改次数${response.data.msg.left_signature_n}`)
                    signature.value = signature_edit.value;
                }
            }
            if (!response.data.msg.avatar_flag) {
                ElMessage.warning("头像剩余修改次数不足！")
            } else {
                ElMessage.success(`头像修改成功！剩余修改次数${response.data.msg.left_avatar_n}`)
                imageUrl.value = URL.createObjectURL(options.file);
            }
        } else if (response.data.status >= 101) {
            // 适配后端的两种error
            if (response.data.msg.avatar) {
                ElMessage.error(response.data.msg.avatar[0]);
            } else {
                ElMessage.error(response.data.msg);
            }

        }
    })
}

const handleChange: UploadProps['onChange'] = (uploadFile: UploadFile, uploadFiles: UploadFiles) => {
    if (!uploadFile.url) {
        uploadFile.url = URL.createObjectURL(uploadFile.raw!)
    }
    imageUrl.value = uploadFile.url;
    avatar_changed.value = true;
}

const handleExceed: UploadProps['onExceed'] = (files) => {
    upload.value!.clearFiles()
    const file = files[0] as UploadRawFile
    file.uid = genFileId()
    upload.value!.handleStart(file)
}

const beforeAvatarUpload: UploadProps['beforeUpload'] = (rawFile) => {
    if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png') {
        ElMessage.error('头像必须为JPG或PNG格式!')
        return false
    } else if (rawFile.size / 1024 / 1024 / 50 > 1.0) {
        ElMessage.error('头像大小不能超过50MB!')
        return false
    }
    return new Promise((resolve, reject) => {
        compressAccurately(rawFile, 256).then(res => {
            res = new File([res], rawFile.name, { type: res.type, lastModified: Date.now() })
            resolve(res)
        })
    })
}















</script>


<style>
.avatar-uploader {
    margin: auto;
    text-align: center;
    margin-top: 30px;

}
</style>









