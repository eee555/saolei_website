<!-- 已弃用 -->
<template>
    <div style="width: 480px;margin: 8px;">
        <el-card :body-style="{ padding: '0px', margin: '8px' }" style="border-radius: 8px;">
            <img 
                v-if="videoMsg.filename.slice(-3) === 'avf'" src="../assets/img/img_arbiter.png"
                style="height: 54px;width: 54px;vertical-align:middle;margin-left: 5px;margin-right: 12px;"
            >
            <img 
                v-if="videoMsg.filename.slice(-3) === 'evf'" src="../assets/img/img_meta.png"
                style="height: 54px;width: 54px;vertical-align:middle;margin-left: 5px;margin-right: 12px;"
            >
            <div style="display: inline-block;vertical-align:middle;width: 360px;text-align:left;">
                <el-row :gutter="5" style="text-align: center;margin-bottom: 5px;">
                    <el-col :span="24">
                        <div class="ep-bg-purple grid-content">
                            {{ videoMsg.filename }}
                        </div>
                    </el-col>
                </el-row>
                <el-row :gutter="5">
                    <el-col :span="11">
                        <div class="ep-bg-purple grid-content">
                            难度：{{ videoMsg.level }}
                        </div>
                    </el-col>
                    <el-col :span="13">
                        <!-- @vue-skip -->
                        <div class="ep-bg-purple grid-content">
                            时间：{{ ms_to_s(videoMsg.timems) }}s
                        </div>
                    </el-col>
                </el-row>
                <el-row :gutter="5">
                    <el-col :span="11">
                        <div class="ep-bg-purple grid-content">
                            3BV：{{ videoMsg.bbbv }}
                        </div>
                    </el-col>
                    <el-col :span="13">
                        <div class="ep-bg-purple grid-content">
                            3BV/s：{{ videoMsg.bvs }}
                        </div>
                    </el-col>
                </el-row>
            </div>
            <span class="close_icon" style="vertical-align: middle;" @click="emit('cancel_this',videoMsg.id)">
                <el-icon size="28px">
                    <CircleCloseFilled />
                </el-icon>
            </span>
        </el-card>
    </div>
</template>
  
<script lang="ts" setup>
// 上传录像的页面，等待上传的录像的卡片
import { onMounted } from 'vue'
import { ElCard, ElIcon, ElRow, ElCol } from 'element-plus';
const emit = defineEmits(['cancel_this', 'logout']);



const { videoMsg } = defineProps({
    videoMsg: {
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
        default() {
            return {
                id: 0,
                filename: "",
                level: "",
                timems: "",
                bbbv: "",
                bvs: "",
            }
        },
    }
})

onMounted(() => {
    // const player = proxy.$store.state.user;


})



// const upload_video_visible = ref(false)





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









