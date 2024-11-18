<!-- 已弃用 -->

<template>
    <span class="text-button" @click="centerDialogVisible = true;">{{ $t('menu.groups') }}</span>
    <el-dialog v-model="centerDialogVisible" title="扫码加入QQ群" width="50%" align-center draggable :lock-scroll="false">
        <div style="text-align: center;">
            <el-image style="border-radius: 20px;" :src="imageGroup1" :fit="'cover'" />
        </div>



        <template #footer>
            <span class="dialog-footer">
                <el-button type="primary" @click="centerDialogVisible = false">
                    确定
                </el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script lang="ts" setup>
// 注册、登录的弹框及右上方按钮
import { onMounted, ref, Ref } from 'vue'
import imageGroup1 from '@/assets/group_1.jpg'


import { useI18n } from 'vue-i18n';
const t = useI18n();

const centerDialogVisible = ref(false);



onMounted(() => {


})







</script>


<style scoped>
a {
    color: blue;
}
</style>
