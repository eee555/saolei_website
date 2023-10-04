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
                                <el-input v-model="realname_edit" placeholder="请输入真实姓名" minlength="2"
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
                        <el-image style="width: 200px; height: 200px;border-radius: 12px;" :src="imageUrl" :fit="'cover'" />
                    </div>
                    <div style="font-size: 30px;margin-top: 10px;margin-bottom: 8px;">{{ username }}</div>
                    <div style="font-size: 20px;margin-bottom: 8px;">{{ realname }}</div>
                    <div style="overflow: auto ;"><strong>个性签名：</strong>{{ signature }}</div>

                    <el-button type="primary" :plain="true" :size="'large'" @click="is_editing = true;"
                        style="font-size: 18px;margin-top: 18px;width: 160px;">修改个人资料</el-button>
                </div>
            </el-aside>
            <el-main>
                <div v-for="(d, idx) in records">
                    <h4 style="margin-bottom: 0px;margin-top: 20px;">{{ table_title[idx] }}模式记录：</h4>
                    <el-table :data="d" style="width: 100%" :header-cell-style="{ 'text-align': 'center' }">
                        <el-table-column type="index" :index="indexMethod" width="100" align="center" />
                        <el-table-column label="time" align="center">
                            <template #default="scope">
                                <el-link href="https://element-plus.org" target="_blank" v-if="scope.row.time">{{
                                    scope.row.time }}</el-link>
                                <span v-else> {{ "999.999" }} </span>
                            </template>
                        </el-table-column>
                        <el-table-column label="3BV/s" align="center">
                            <template #default="scope">
                                <el-link href="https://element-plus.org" target="_blank" v-if="scope.row.bvs">{{
                                    scope.row.bvs }}</el-link>
                                <span v-else> {{ "0.000" }} </span>
                            </template>
                        </el-table-column>
                        <el-table-column label="STNB" align="center">
                            <template #default="scope">
                                <el-link href="https://element-plus.org" target="_blank" v-if="scope.row.stnb">{{
                                    scope.row.stnb }}</el-link>
                                <span v-else> {{ "0.000" }} </span>
                            </template>
                        </el-table-column>
                        <el-table-column label="IOE" align="center">
                            <template #default="scope">
                                <el-link href="https://element-plus.org" target="_blank" v-if="scope.row.ioe">{{
                                    scope.row.ioe }}</el-link>
                                <span v-else> {{ "0.000" }} </span>
                            </template>
                        </el-table-column>
                        <el-table-column label="path" align="center">
                            <template #default="scope">
                                <el-link href="https://element-plus.org" target="_blank" v-if="scope.row.path">{{
                                    scope.row.path }}</el-link>
                                <span v-else> {{ "99999.9" }} </span>
                            </template>
                        </el-table-column>
                    </el-table>
                </div>
            </el-main>
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
const avatar_changed = ref(false);
import { Record, RecordBIE } from "@/utils/common/structInterface";

//编辑前的
const username = ref("");
const realname = ref("");
const signature = ref("");

//编辑状态时的
const realname_edit = ref("");
const signature_edit = ref("");

// 是否在编辑的标识
const is_editing = ref(false);

// 个人纪录表格
const records = ref<Record[][]>([]);
const table_title = ["标准", "盲扫", "无猜", "递归"];

const indexMethod = (index: number) => {
    return ["", "初级", "中级", "高级"][index + 1]
}

onMounted(() => {
    const player = proxy.$store.state.player;
    // username.value = player.name;

    // 把左侧的头像、姓名、个性签名请求过来
    proxy.$axios.get('/msuser/info/',
        {
            params: {
                id: player.id,
            }
        }
    ).then(function (response) {
        const data = response.data;
        username.value = data.realname;
        signature.value = data.signature;
        realname_edit.value = data.realname;
        signature_edit.value = data.signature;
        // console.log(imageUrl);
        imageUrl.value = "data:image/;base64," + data.avatar;
        // console.log(imageUrl);
        records.value.push(trans_record(JSON.parse(data.std_record)));
        records.value.push(trans_record(JSON.parse(data.nf_record)));
        records.value.push(trans_record(JSON.parse(data.ng_record)));
        records.value.push(trans_record(JSON.parse(data.dg_record)));
        console.log(records.value[0]);
        console.log(666);


    })

    // 再把个人纪录请求过来
    // std_record
})

// 把记录数据转一下嵌套的结构，做数据格式的适配
function trans_record(r: RecordBIE): Record[] {
    const record: Record[] = [];
    for (let i = 0; i < r.time.length; i++) {
        record.push({
            time: r.time[i],
            bvs: r.bvs[i],
            stnb: r.stnb[i],
            ioe: r.ioe[i],
            path: r.path[i],
            time_id: r.time_id[i],
            bvs_id: r.bvs_id[i],
            stnb_id: r.stnb_id[i],
            ioe_id: r.ioe_id[i],
            path_id: r.path_id[i],
        })
    }
    return record;
}

// 修改确认按钮的回调，改过图片就走unload的回调上传，否则就按钮本身回调上传
const upload_info = () => {
    is_editing.value = false;
    if (avatar_changed.value) {
        upload.value!.submit();
    } else {
        let params = new FormData()
        params.append('realname', realname_edit.value)
        params.append('signature', signature_edit.value)
        proxy.$axios.post('/msuser/update/',
            params,
        ).then(function (response) {
            if (response.data.status == 100) {
                ElMessage.success("信息更新成功！")
                username.value = realname_edit.value;
                signature.value = signature_edit.value;
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
            console.log(options.file);
            ElMessage.success("信息更新成功！")
            username.value = realname_edit.value;
            signature.value = signature_edit.value;
            imageUrl.value = URL.createObjectURL(options.file);
        } else if (response.data.status >= 101) {
            ElMessage.error(response.data.msg)
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
    // console.log(rawFile);

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









