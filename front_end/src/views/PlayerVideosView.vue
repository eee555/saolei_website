<template>
    <el-button @click="downloadCSV(generateArbiterCSV(store.player.id))" v-if="false && !store.player.loading">
        {{ $t('profile.exportArbiterCSV') }}&nbsp;
        <el-tooltip :content="$t('profile.exportArbiterCSVTooltip')" raw-content>
            <el-icon v-if="local.tooltip_show">
                <QuestionFilled />
            </el-icon>
        </el-tooltip>
    </el-button>
    <el-card class="box-card" body-style="" style="max-height: 800px; overflow: auto; margin-top:5px">
        <el-skeleton animated v-show="store.player.loading" :rows="8" />
        <VideoList :videos="store.player.videos" :need_player_name="false" reverse></VideoList>
    </el-card>
</template>

<script lang="ts" setup>
// 个人主页的个人所有录像部分
import { onMounted, ref, Ref } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
// import { genFileId, ElMessage } from 'element-plus'
import VideoList from '@/components/VideoList.vue';
// import { fa } from 'element-plus/es/locale';
import { local, store } from '../store'

function generateArbiterCSV(data: any) {
    let csvdata = ['Day,Month,Year,Hour,Min,Sec,mode,Time,BBBV,BBBVs,style,cell0,cell1,cell2,cell3,cell4,cell5,cell6,cell7,cell8,Lcl,Rcl,Dcl,Leff,Reff,Deff,Openings,Islands,Path,GZiNi,HZiNi']
    for (let v of data) {
        if (v.mode != 'std' && v.mode != 'nf') continue;
        let date = new Date(v.upload_time);
        let row: any[] = [date.getUTCDate(), date.getUTCMonth() + 1, date.getUTCFullYear(), date.getUTCHours(), date.getUTCMinutes(), date.getUTCSeconds()];
        switch (v.level) {
            case 'e': row.push(3); break;
            case 'i': row.push(2); break;
            case 'b': row.push(1); break;
            default: console.error('未知级别');
        }
        row.push((v.timems / 1000).toFixed(2));
        row.push(v.bv);
        row.push(v.bvs.toFixed(2));

        if (v.video__flag == 0) row.push('NF');
        else row.push('Flag');

        row.push(v.video__cell0, v.video__cell1, v.video__cell2, v.video__cell3, v.video__cell4, v.video__cell5, v.video__cell6, v.video__cell7, v.video__cell8)
        row.push(v.video__left, v.video__right, v.video__double, 0, 0, 0)
        row.push(v.video__op, v.video__isl)
        row.push(Math.round(v.video__path))
        row.push(0, 0)
        csvdata.push(row.join())
    }
    return csvdata.join('\n');
}

// Credit: ChatGPT
function downloadCSV(csv: string) {
    // Create a Blob from the CSV data
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);

    // Create a temporary anchor element
    const a = document.createElement('a');
    a.href = url;
    a.download = 'stats_csv.csv'; // Set the file name

    // Append the anchor to the body
    document.body.appendChild(a);
    a.click(); // Trigger the download
    document.body.removeChild(a); // Remove the anchor after download

    // Release the object URL
    URL.revokeObjectURL(url);
}

</script>


<style>
.avatar-uploader {
    margin: auto;
    text-align: center;
    margin-top: 30px;

}
</style>
