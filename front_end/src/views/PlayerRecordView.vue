<template>
    <base-card-large>
        <el-skeleton v-show="loading" animated style="margin-top: 0px;" :rows="8" />
        <div v-for="(d, idx) in records" style="margin-top: -10px;">
            <h4>{{ t(table_title[idx]) }}{{ t('profile.records.modeRecord') }}</h4>
            <el-table :data="d" style="width: 100%;" :header-cell-style="{ 'text-align': 'center' }">
                <el-table-column type="index" :index="indexMethod" width="100" align="center" />

                <el-table-column label="time" align="center">
                    <template #default="scope">
                        <PreviewNumber :id="scope.row.timems_id" :text="ms_to_s(scope.row.timems)" />
                    </template>
                </el-table-column>

                <el-table-column label="3BV/s" align="center">
                    <template #default="scope">
                        <PreviewNumber :id="scope.row.bvs_id" :text="scope.row.bvs.toFixed(3)" />
                    </template>
                </el-table-column>

                <el-table-column label="STNB" align="center">
                    <template #default="scope">
                        <PreviewNumber :id="scope.row.stnb_id" :text="scope.row.stnb.toFixed(3)" />
                    </template>
                </el-table-column>

                <el-table-column label="IOE" align="center">
                    <template #default="scope">
                        <PreviewNumber :id="scope.row.ioe_id" :text="scope.row.ioe.toFixed(3)" />
                    </template>
                </el-table-column>

                <el-table-column label="path" align="center">
                    <template #default="scope">
                        <PreviewNumber :id="scope.row.path_id" :text="scope.row.path.toFixed(3)" />
                    </template>
                </el-table-column>
            </el-table>
        </div>
    </base-card-large>
</template>

<script lang="ts" setup>
// 个人主页的个人纪录部分
import { ref, nextTick } from 'vue'
import { ElTable, ElTableColumn, ElSkeleton } from 'element-plus';
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import PreviewNumber from '@/components/PreviewNumber.vue';
import BaseCardLarge from '@/components/common/BaseCardLarge.vue';
import { ElMessage } from 'element-plus'
const { proxy } = useCurrentInstance();
import { Record, RecordBIE } from "@/utils/common/structInterface";
import { ms_to_s } from "@/utils"
import { store } from '../store'

import { useI18n } from 'vue-i18n';
const { t } = useI18n();

const loading = ref(true)

//编辑前的
const userid = ref("");
const username = ref("");

// 个人纪录表格
const records = ref<Record[][]>([]);
const table_title = ['common.mode.std', 'common.mode.nf', 'common.mode.ng', 'common.mode.dg'];

const indexMethod = (index: number) => {
    return ["", t('common.level.b'), t('common.level.i'), t('common.level.e')][index + 1]
}

// 此处和父组件配合，等一下从store里获取用户的id
nextTick(() => {

    // 把左侧的头像、姓名、个性签名、记录请求过来
    proxy.$axios.get('/msuser/records/',
        {
            params: {
                id: store.player.id,
            },
        },
    ).then(function (response) {
        const data = response.data;
        if (data.status > 100) {
            loading.value = false;
            ElMessage.error({ message: '不知哪里出现了问题', offset: 68 });
        } else {
            userid.value = data.id;
            username.value = data.realname;
            records.value.push(trans_record(JSON.parse(data.std_record)));
            records.value.push(trans_record(JSON.parse(data.nf_record)));
            records.value.push(trans_record(JSON.parse(data.ng_record)));
            records.value.push(trans_record(JSON.parse(data.dg_record)));
            loading.value = false;
        }


    })

    // 再把个人纪录请求过来
    // std_record
})

// 把记录数据转一下嵌套的结构，做数据格式的适配
function trans_record(r: RecordBIE): Record[] {
    const record: Record[] = [];
    for (let i = 0; i < r.timems.length; i++) {
        record.push({
            timems: r.timems[i],
            bvs: r.bvs[i],
            stnb: r.stnb[i],
            ioe: r.ioe[i],
            path: r.path[i],
            timems_id: r.timems_id[i],
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
