<template>
    <div style="width: 480px;margin: 8px;">
        <el-card :body-style="{ padding: '0px', margin: '8px' }" style="border-radius: 8px;">
            <img v-if="video_msg.filename.slice(-3) === 'avf'" src="../assets/img/img_arbiter.png"
                style="height: 54px;width: 54px;vertical-align:middle;margin-left: 5px;margin-right: 12px;" />
            <img v-if="video_msg.filename.slice(-3) === 'evf'" src="../assets/img/img_meta.png"
                style="height: 54px;width: 54px;vertical-align:middle;margin-left: 5px;margin-right: 12px;" />
            <div style="display: inline-block;vertical-align:middle;width: 360px;text-align:left;">
                <el-row :gutter="5" style="text-align: center;margin-bottom: 5px;">
                    <el-col :span="24">
                        <div class="grid-content ep-bg-purple">{{ video_msg.filename }}</div>
                    </el-col>
                </el-row>
                <el-row :gutter="5">
                    <el-col :span="11">
                        <div class="grid-content ep-bg-purple">难度：{{ video_msg.level }}</div>
                    </el-col>
                    <el-col :span="13">
                        <div class="grid-content ep-bg-purple">时间：{{ ms_to_s(video_msg.timems) }}s</div>
                    </el-col>
                </el-row>
                <el-row :gutter="5">
                    <el-col :span="11">
                        <div class="grid-content ep-bg-purple">3BV：{{ video_msg.bbbv }}</div>
                    </el-col>
                    <el-col :span="13">
                        <div class="grid-content ep-bg-purple">3BV/s：{{ video_msg.bvs }}</div>
                    </el-col>
                </el-row>
            </div>
            <span @click="emit('cancel_this',video_msg.id)" class="close_icon" style="vertical-align: middle;">
                <el-icon size="28px">
                    <CircleCloseFilled />
                </el-icon>
            </span>
        </el-card>
    </div>
</template>
  
<script lang="ts" setup>
// 上传录像的页面，等待上传的录像的卡片
import { onMounted, ref, Ref } from 'vue'
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import { ms_to_s } from '@/utils';
const { proxy } = useCurrentInstance();
const emit = defineEmits(['cancel_this', 'logout']);



const { video_msg } = defineProps({
    video_msg: {
        type: Object as () => {
            // 在待上传列表中排第几个
            id: number,
            // 文件名，后缀提示录像的类型，按类型显示图标
            filename: string,
            level: string;
            timems: string;
            bbbv: string;
            bvs: string;
        },
        default: {
            id: 0,
            filename: "",
            level: "",
            timems: "",
            bbbv: "",
            bvs: "",
        }
    }
})

onMounted(() => {
    // const player = proxy.$store.state.user;


})



// const upload_video_visibile = ref(false)





</script>


<style>
/* input:invalid {
    outline: 2px solid rgb(167, 11, 11);
    border-radius: 3px;
} */


.close_icon:hover {
    color: #4CA4FF;
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









