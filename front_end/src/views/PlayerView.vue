<template>
    <div class="common-layout">
        <el-container>
            <el-aside width="30%">
                <div v-if="is_editing">
                    <el-upload ref="upload" class="avatar-uploader" action="#" :limit="1" :show-file-list="false"
                        :auto-upload="false" :on-exceed="handleExceed" :on-change="handleChange"
                        :before-upload="beforeAvatarUpload" :http-request="handleAvatarUpload"
                        style="width: 200px; height: 200px;border-radius: 12px;">
                        <el-image style="width: 200px; height: 200px;border-radius: 12px;" v-if="imageUrl"
                            :src="imageUrl" :fit="'cover'" />
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
                        <el-image style="width: 200px; height: 200px;border-radius: 12px;" :src="imageUrl"
                            :fit="'cover'" />
                    </div>
                    <div style="font-size: 30px;margin-top: 10px;margin-bottom: 8px;">
                        {{ username }}
                        <span style="font-size: 18px; color: #555;">id: {{ userid }}</span>
                    </div>
                    <div style="font-size: 20px;margin-bottom: 8px;">{{ realname }}</div>
                    <div style="overflow: auto ;"><strong>个性签名：</strong>{{ signature }}</div>
                    <!-- <div style="overflow: auto ;">人气：{{ popularity }}</div> -->

                    <el-button v-show="show_edit_button" type="primary" :plain="true" :size="'large'"
                        @click="is_editing = true; visible = true;"
                        style="font-size: 18px;margin-top: 18px;width: 160px;">修改个人资料</el-button>
                </div>

                <el-dialog v-model="visible" title="请注意" width="50%" align-center draggable :lock-scroll="false">
                    <ul>
                        <li>本站实行实名制，改名前无法上传录像。改名机会有且仅有一次，请慎重填写！如果姓名填错，请联系管理员。</li>
                        <li>填写真实姓名后您将获得一个和真实姓名对应的默认标识。与默认标识不同的标识需要通过人工审核。</li>
                        <li>标准高级sub200之后才能修改个性签名和头像。用户的头像、个性签名的初始修改次数为2次，之后每年获得一次。</li>
                        <li>个人资料需遵守国家法律法规。</li>
                    </ul>

                    <template #footer>
                        <span class="dialog-footer">
                            <el-button type="primary" @click="visible = false">
                                确定
                            </el-button>
                        </span>
                    </template>
                </el-dialog>
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
// 我的地盘页面
import { onMounted, ref, Ref, defineAsyncComponent, computed } from 'vue'
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
const popularity = ref("");

//编辑状态时的
const realname_edit = ref("");
const signature_edit = ref("");

// 是否在编辑的标识
const is_editing = ref(false);
// 弹窗的可见性
const visible = ref(false);

// 标签默认切在第一页
const activeName = ref('first')
// const player = proxy.$store.state.player;
const player = {
    id: -1,
};
// console.log(player);

// 上传可能失败，备份旧的头像
let imageUrlOld: any;

const user = proxy.$store.state.user;
let show_edit_button: boolean;

onMounted(() => {
    // 把左侧的头像、姓名、个性签名、记录请求过来

    let player_id = +proxy.$route.params.id;
    if (Number.isInteger(player_id) && player_id >= 1) {
        player.id = player_id;
        localStorage.setItem("player", JSON.stringify({ "id": player_id }));
    } else {
        player.id = JSON.parse(localStorage.getItem("player") as string).id as number;
    }
    show_edit_button = player.id == user.id;

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
        popularity.value = data.popularity;
        realname_edit.value = data.realname;
        signature_edit.value = data.signature;
        // console.log(imageUrl);
        if (data.avatar) {
            imageUrl.value = "data:image/;base64," + data.avatar;
            imageUrlOld = "data:image/;base64," + data.avatar;
        }
        // console.log(imageUrl);
        loading.value = false;

    })

    // 再把个人纪录请求过来
    // std_record
})


// 向后台发送请求修改姓名
const post_update_realname = (r: string) => {
    let params = new FormData()
    params.append('realname', r)
    proxy.$axios.post('/msuser/update_realname/',
        params,
    ).then(function (response) {
        if (response.data.status == 100) {
            ElMessage.success(`姓名修改成功！剩余修改次数${response.data.msg.n}`)
            realname.value = realname_edit.value;
            proxy.$store.commit('updateUserRealname', realname.value);
            if (player.id == user.id) {
                // 访问用户自己的地盘
                // 解决改名后，个人录像列表里名字不能立即改过来
                // localStorage.setItem("player", JSON.stringify({ "id": player.id, "realname": realname.value }));
                localStorage.setItem("player", JSON.stringify({ "id": player.id }));
            }

            // proxy.$store.commit('updateUser', response.data.msg);// 当前登录用户
            // proxy.$store.commit('updatePlayer', response.data.msg);// 看我的地盘看谁的
            // localStorage.setItem("player", JSON.stringify(response.data.msg));

        } else if (response.data.status >= 101) {
            console.log(response.data);
            realname_edit.value = realname.value;
            ElMessage.error(response.data.msg)
        }
    }).catch(() => {
        ElMessage.error("无法连接到服务器！")
    })
}

// 向后台发送请求修改头像
const post_update_avatar = (a: File) => {
    let params = new FormData()
    params.append('avatar', a)
    proxy.$axios.post('/msuser/update_avatar/',
        params,
    ).then(function (response) {
        if (response.data.status == 100) {
            ElMessage.success(`头像修改成功！剩余修改次数${response.data.msg.n}`)
            imageUrl.value = URL.createObjectURL(a);
        } else if (response.data.status >= 101) {
            ElMessage.error(response.data.msg)
            imageUrl.value = imageUrlOld;
        }
    }).catch(() => {
        ElMessage.error("无法连接到服务器！")
    })
}

// 向后台发送请求修改签名
const post_update_signature = (s: string) => {
    let params = new FormData()
    params.append('signature', s)
    proxy.$axios.post('/msuser/update_signature/',
        params,
    ).then(function (response) {
        // console.log(response.data);

        if (response.data.status == 100) {
            ElMessage.success(`个性签名修改成功！剩余修改次数${response.data.msg.n}`)
            signature.value = signature_edit.value;
        } else if (response.data.status >= 101) {
            ElMessage.error(response.data.msg)
            signature_edit.value = signature.value;
        }
    }).catch(() => {
        ElMessage.error("无法连接到服务器！")
    })
}

// 修改确认按钮的回调，改过头像就走unload的回调上传，否则就按钮本身回调上传
const upload_info = () => {
    is_editing.value = false;
    if (avatar_changed.value) {
        upload.value!.submit();
    } else {
        // 没改头像，只改了姓名或个性签名，或什么也没改
        if (realname_edit.value != realname.value) {
            post_update_realname(realname_edit.value);
        }
        if (signature_edit.value != signature.value) {
            post_update_signature(signature_edit.value);
        }
    }
}

// 把头像、姓名、个性签名传上去。至少头像改过了。
const handleAvatarUpload = async (options: UploadRequestOptions) => {

    // console.log("****" + realname_edit.value);
    // console.log("----" + realname.value);
    if (realname_edit.value != realname.value) {
        post_update_realname(realname_edit.value);
    }
    // console.log("34554" + signature_edit.value);
    // console.log("5654" + signature.value);

    if (signature_edit.value != signature.value) {
        post_update_signature(signature_edit.value);
    }
    post_update_avatar(options.file);
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
