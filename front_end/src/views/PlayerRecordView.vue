<template>
    <el-card class="box-card" body-style="padding-top:0px;padding-left:20px;padding-right:12px;">
        <el-skeleton animated style="margin-top: 20px;" v-show="loading" :rows="8" />
        <div v-for="(d, idx) in records">
            <h4 style="margin-bottom: 0px;margin-top: 20px;">{{ table_title[idx] }}模式记录：</h4>
            <el-table :data="d" style="width: 100%" :header-cell-style="{ 'text-align': 'center' }">
                <el-table-column type="index" :index="indexMethod" width="100" align="center" />

                <el-table-column label="time" align="center">
                    <template #default="scope">
                        <el-popover placement="bottom" :width="165" :disabled="!scope.row.time_id"
                            popper-style="background-color:rgba(250,250,250,0.38);" :hide-after="0">
                            <div>
                                <PreviewDownload :id="scope.row.time_id"></PreviewDownload>
                            </div>
                            <template #reference>
                                <el-link href="" target="_blank" v-if="scope.row.time_id">{{
                                    scope.row.time.toFixed(3) }}</el-link>
                                <span v-else> {{ "999.999" }} </span>
                            </template>
                        </el-popover>
                    </template>
                </el-table-column>

                <el-table-column label="3BV/s" align="center">
                    <template #default="scope">
                        <el-popover placement="bottom" :width="165" :disabled="!scope.row.bvs_id"
                            popper-style="background-color:rgba(250,250,250,0.38);" :hide-after="0">
                            <div>
                                <PreviewDownload :id="scope.row.bvs_id"></PreviewDownload>
                            </div>
                            <template #reference>
                                <el-link href="" target="_blank" v-if="scope.row.bvs_id">{{
                                    scope.row.bvs.toFixed(3) }}</el-link>
                                <span v-else> {{ "0.000" }} </span>
                            </template>
                        </el-popover>
                    </template>
                </el-table-column>

                <el-table-column label="STNB" align="center">
                    <template #default="scope">
                        <el-popover placement="bottom" :width="165" :disabled="!scope.row.stnb_id"
                            popper-style="background-color:rgba(250,250,250,0.38);" :hide-after="0">
                            <div>
                                <PreviewDownload :id="scope.row.stnb_id"></PreviewDownload>
                            </div>
                            <template #reference>
                                <el-link href="" target="_blank" v-if="scope.row.stnb_id">{{
                                    scope.row.stnb.toFixed(3) }}</el-link>
                                <span v-else> {{ "0.000" }} </span>
                            </template>
                        </el-popover>
                    </template>
                </el-table-column>

                <el-table-column label="IOE" align="center">
                    <template #default="scope">
                        <el-popover placement="bottom" :width="165" :disabled="!scope.row.ioe_id"
                            popper-style="background-color:rgba(250,250,250,0.38);" :hide-after="0">
                            <div>
                                <PreviewDownload :id="scope.row.ioe_id"></PreviewDownload>
                            </div>
                            <template #reference>
                                <el-link href="" target="_blank" v-if="scope.row.ioe_id">{{
                                    scope.row.ioe.toFixed(3) }}</el-link>
                                <span v-else> {{ "0.000" }} </span>
                            </template>
                        </el-popover>
                    </template>
                </el-table-column>

                <el-table-column label="path" align="center">
                    <template #default="scope">
                        <el-popover placement="bottom" :width="165" :disabled="!scope.row.path_id"
                            popper-style="background-color:rgba(250,250,250,0.38);" :hide-after="0">
                            <div>
                                <PreviewDownload :id="scope.row.path_id"></PreviewDownload>
                            </div>
                            <template #reference>
                                <el-link href="" target="_blank" v-if="scope.row.path_id">{{
                                    scope.row.path.toFixed(3) }}</el-link>
                                <span v-else> {{ "0.000" }} </span>
                            </template>
                        </el-popover>
                    </template>
                </el-table-column>
            </el-table>
        </div>
    </el-card>
</template>
  
<script lang="ts" setup>
// 个人主页的个人纪录部分
import { onMounted, ref, Ref, defineEmits } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import PreviewDownload from '@/components/PreviewDownload.vue';
const { proxy } = useCurrentInstance();
import { genFileId, ElMessage } from 'element-plus'
import type { UploadInstance, UploadProps, UploadRawFile, UploadFile, UploadFiles, UploadRequestOptions } from 'element-plus'
const upload = ref<UploadInstance>()
import { Plus } from '@element-plus/icons-vue'
// const imageUrl = ref(require('@/assets/person.png'))
const avatar_changed = ref(false);
import { Record, RecordBIE } from "@/utils/common/structInterface";
import { compress, compressAccurately } from 'image-conversion';

const loading = ref(true)

//编辑前的
const userid = ref("");
const username = ref("");
// const realname = ref("");
// const signature = ref("");

//编辑状态时的
// const realname_edit = ref("");
// const signature_edit = ref("");


// 个人纪录表格
const records = ref<Record[][]>([]);
const table_title = ["标准", "盲扫", "无猜", "递归"];

const indexMethod = (index: number) => {
    return ["", "初级", "中级", "高级"][index + 1]
}

onMounted(() => {
    const player = proxy.$store.state.player;
    // username.value = player.name;

    // 把左侧的头像、姓名、个性签名、记录请求过来
    proxy.$axios.get('/msuser/records/',
        {
            params: {
                id: player.id,
            }
        }
    ).then(function (response) {
        const data = response.data;
        userid.value = data.id;
        username.value = data.realname;
        // signature.value = data.signature;
        // realname_edit.value = data.realname;
        // signature_edit.value = data.signature;
        
        // if (data.avatar) {
        //     imageUrl.value = "data:image/;base64," + data.avatar;
        // }
        // console.log(imageUrl);
        records.value.push(trans_record(JSON.parse(data.std_record)));
        records.value.push(trans_record(JSON.parse(data.nf_record)));
        records.value.push(trans_record(JSON.parse(data.ng_record)));
        records.value.push(trans_record(JSON.parse(data.dg_record)));
        // console.log(records.value[0]);
        // console.log(666);
        loading.value = false;

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








</script>


<style>
.avatar-uploader {
    margin: auto;
    text-align: center;
    margin-top: 30px;

}
</style>









