<template>
    <div>
        <el-container>
            <el-aside width="200px">
                <div v-if="is_editing">
                    <el-upload
                        ref="upload" class="avatar-uploader" action="#" :limit="1" :show-file-list="false"
                        :auto-upload="false" :on-exceed="handleExceed" :on-change="handleChange"
                        :before-upload="beforeAvatarUpload" :http-request="handleAvatarUpload"
                        style="width: 200px; height: 200px;border-radius: 20px;"
                    >
                        <el-image
                            v-if="imageUrl" style="width: 200px; height: 200px;border-radius: 20px;"
                            :src="imageUrl" :fit="'cover'"
                        />
                        <base-icon-add v-else />
                    </el-upload>
                    <div style="font-size: 14px;color: #AAA;text-align: center;">
                        {{ t('profile.changeAvatar') }}
                    </div>
                    <div style="margin-top: 12px;margin-bottom: 4px;">
                        {{ t('profile.realname') }}
                    </div>
                    <div>
                        <el-input
                            v-model="realname_edit" :placeholder="t('profile.realnameInput')" minlength="2"
                            maxlength="100"
                        />
                    </div>
                    <div style="margin-top: 12px;margin-bottom: 4px;">
                        {{ t('profile.signature') }}
                    </div>
                    <div>
                        <el-input
                            v-model="signature_edit" :placeholder="t('profile.signatureInput')" minlength="0"
                            maxlength="188" type="textarea" :rows="8"
                        />
                    </div>

                    <button class="edit_button_ok" @click="upload_info">
                        {{ t('common.button.confirm') }}
                    </button>
                    <button class="edit_button_cancel" @click="is_editing = false;">
                        {{ t('common.button.cancel')
                        }}
                    </button>
                </div>

                <div v-else>
                    <div :key="'cover'" class="avatar-uploader">
                        <el-image
                            style="width: 200px; height: 200px;border-radius: 20px;" :src="imageUrl"
                            :fit="'cover'"
                        />
                    </div>
                    <div style="font-size: 30px;margin-top: 10px;">
                        {{ username }}
                        <span style="font-size: 18px; color: #555;">id: {{ userid }}</span>
                    </div>
                    <div style="font-size: 16px;margin-bottom: 12px;color: #555;">
                        <!-- <span class="flag-icon flag-icon-cn"/> -->
                        {{ realname }}
                    </div>
                    <div style="overflow: auto ;font-size: 16px;margin-bottom: 12px;text-align: justify;">
                        {{ signature }}
                    </div>
                    <button v-show="show_edit_button" class="edit_button" @click="is_editing = true; visible = true;">
                        {{
                            t('profile.change') }}
                    </button>
                    <!-- <div style="overflow: auto ;">人气：{{ popularity }}</div> -->
                </div>
            </el-aside>

            <el-main>
                <el-tabs v-model="activeName" style="overflow: auto;">
                    <el-tab-pane
                        :label="t('profile.profile.title')" name="profile" :lazy="true"
                        style="overflow: auto;"
                    >
                        <PlayerProfileView :key="store.player.id" />
                    </el-tab-pane>
                    <el-tab-pane :label="t('profile.records.title')" name="record" :lazy="true">
                        <PlayerRecordView :key="store.player.id" />
                    </el-tab-pane>
                    <el-tab-pane :label="t('profile.videos')" name="video" :lazy="true">
                        <PlayerVideosView :key="store.player.id" />
                    </el-tab-pane>
                    <el-tab-pane
                        v-if="`${store.user.id}` == userid" :label="t('profile.upload.title')" name="upload"
                        :lazy="true"
                    >
                        <UploadView :identifiers="store.user.identifiers" />
                    </el-tab-pane>
                </el-tabs>
            </el-main>
        </el-container>
    </div>
</template>

<script lang="ts" setup>
// 我的地盘页面
import { defineAsyncComponent, onMounted, ref, watch } from 'vue'
import { ElContainer, ElAside, ElMain, ElTabs, ElTabPane, ElImage, ElInput, ElUpload } from 'element-plus';
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const PlayerRecordView = defineAsyncComponent(() => import('@/views/PlayerRecordView.vue'));
const PlayerVideosView = defineAsyncComponent(() => import('@/views/PlayerVideosView.vue'));
const PlayerProfileView = defineAsyncComponent(() => import('@/views/PlayerProfileView.vue'));
const UploadView = defineAsyncComponent(() => import('@/views/UploadView.vue'));
import "../../node_modules/flag-icon-css/css/flag-icons.min.css";

const { proxy } = useCurrentInstance();
import { genFileId, ElMessage } from 'element-plus'
import type { UploadInstance, UploadProps, UploadRawFile, UploadFile, UploadFiles, UploadRequestOptions } from 'element-plus'
const upload = ref<UploadInstance>()
import imageUrlDefault from '@/assets/person.png'
const imageUrl = ref(imageUrlDefault)
const avatar_changed = ref(false);
import { compressAccurately } from 'image-conversion';
import { store } from '../store'

import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { UserProfile } from '@/utils/userprofile';
import { unknownErrorNotification } from '@/components/Notifications';
import BaseIconAdd from '@/components/common/BaseIconAdd.vue';
const { t } = useI18n();
const route = useRoute()

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
const activeName = ref('profile')
const player = {
    id: -1,
};

// 上传可能失败，备份旧的头像
let imageUrlOld: any;

// const user = store.user;
let show_edit_button: boolean;

function refresh() {
    const player_id = +proxy.$route.params.id;
    // http://localhost:8080/#/player/1
    // 首先看url里有没有带参，如果有，就访问这个用户；其次看store里有没有用户id。

    if (Number.isInteger(player_id) && player_id >= 1) {
        player.id = player_id;
        store.player.id = player_id;
        // localStorage.setItem("player", JSON.stringify({ "id": player_id }));
    } else {
        // player.id = JSON.parse(localStorage.getItem("player") as string).id as number;
        player.id = store.player.id;
    }
    show_edit_button = player.id == store.user.id;

    proxy.$axios.get('/msuser/info/',
        {
            params: {
                id: player.id,
            }
        }
    ).then(function (response) {
        const data = response.data;
        store.player = new UserProfile(data);

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
    }).catch(unknownErrorNotification);
}

onMounted(refresh)
watch(route, refresh) // 解决切换url不刷新的问题


// 向后台发送请求修改姓名
const post_update_realname = (r: string) => {
    const params = new FormData()
    params.append('realname', r)
    proxy.$axios.post('/msuser/update_realname/',
        params,
    ).then(function (response) {
        if (response.data.status == 100) {
            ElMessage.success({ message: t('profile.msg.realnameChange', [response.data.msg.n]), offset: 68 });

            realname.value = realname_edit.value;
            store.user.realname = realname.value;
            if (player.id == store.user.id) {
                // 访问用户自己的地盘
                // 解决改名后，个人录像列表里名字不能立即改过来
                // localStorage.setItem("player", JSON.stringify({ "id": player.id, "realname": realname.value }));
                localStorage.setItem("player", JSON.stringify({ "id": player.id }));
            }

        } else if (response.data.status >= 101) {
            realname_edit.value = realname.value;
            ElMessage.error({ message: response.data.msg, offset: 68 });
        }
    }).catch(() => {
        ElMessage.error({ message: t('common.msg.connectionFail'), offset: 68 });
    })
}

// 向后台发送请求修改头像
const post_update_avatar = (a: File) => {
    const params = new FormData()
    params.append('avatar', a)
    proxy.$axios.post('/msuser/update_avatar/',
        params,
    ).then(function (response) {
        if (response.data.status == 100) {
            ElMessage.success({ message: t('profile.msg.avatarChange', [response.data.msg.n]), offset: 68 });
            imageUrl.value = URL.createObjectURL(a);
        } else if (response.data.status >= 101) {
            ElMessage.error({ message: response.data.msg, offset: 68 });
            imageUrl.value = imageUrlOld;
        }
    }).catch(() => {
        ElMessage.error({ message: t('common.msg.connectionFail'), offset: 68 });
    })
}

// 向后台发送请求修改签名
const post_update_signature = (s: string) => {
    const params = new FormData()
    params.append('signature', s)
    proxy.$axios.post('/msuser/update_signature/',
        params,
    ).then(function (response) {
        // console.log(response.data);

        if (response.data.status == 100) {
            ElMessage.success({ message: t('profile.msg.signatureChange', [response.data.msg.n]), offset: 68 });
            signature.value = signature_edit.value;
        } else if (response.data.status >= 101) {
            ElMessage.error({ message: response.data.msg, offset: 68 });
            signature_edit.value = signature.value;
        }
    }).catch(() => {
        ElMessage.error({ message: t('common.msg.connectionFail'), offset: 68 });
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
    if (realname_edit.value != realname.value) {
        post_update_realname(realname_edit.value);
    }

    if (signature_edit.value != signature.value) {
        post_update_signature(signature_edit.value);
    }
    post_update_avatar(options.file);
}

const handleChange: UploadProps['onChange'] = (uploadFile: UploadFile, _uploadFiles: UploadFiles) => {
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
        ElMessage.error({ message: t('profile.msg.avatarFormat'), offset: 68 });
        return false
    } else if (rawFile.size / 1024 / 1024 / 50 > 1.0) {
        ElMessage.error({ message: t('profile.msg.avatarFilesize'), offset: 68 });
        return false
    }
    return new Promise((resolve, _reject) => {
        // 此处会报错net::ERR_FILE_NOT_FOUND，但头像依然能更新成功
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

.edit_button {
    font-size: 14px;
    margin-top: 2px;
    width: 200px;
    height: 31px;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    margin-bottom: 12px;
}

.edit_button:hover {
    background-color: rgb(233, 233, 233);
    /* 鼠标悬停时改变背景颜色为浅灰色 */
}


.edit_button_ok {
    font-size: 14px;
    margin-top: 12px;
    height: 31px;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    margin-right: 3px;
    background-color: #1F883D;
    color: #fff;
}

.edit_button_ok:hover {
    background-color: #238f42;
    /* 鼠标悬停时改变背景颜色为浅灰色 */
}

.edit_button_cancel {
    font-size: 14px;
    margin-top: 12px;
    height: 31px;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    /* margin-right: 3px; */
    /* background-color:#1F883D; */
}

.edit_button_cancel:hover {
    background-color: rgb(233, 233, 233);
    /* 鼠标悬停时改变背景颜色为浅灰色 */
}
</style>
