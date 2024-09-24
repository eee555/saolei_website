<template>
    <!-- <span class="text-button" @click="centerDialogVisible = true;"> -->
    <el-link @click="centerDialogVisible = true;">
        {{ $t('common.software.software_download') }}
    </el-link>
    <el-dialog v-model="centerDialogVisible" :title="$t('common.software.software_download')" width="50%" align-center
        draggable :lock-scroll="false">
        <ul>
            <li><a style="color: blue;" target="_blank" href="https://fff666.top/download/Metaminesweeper-v3.1.9.zip">
                    {{ $t('common.software.metasweeper') }} v3.1.9</a> {{ $t('common.software.download_link') }} 1<br>
                <a style="color: blue;" target="_blank"
                    href="https://github.com/eee555/Solvable-Minesweeper/releases/download/3.1.9/Metaminesweeper-v3.1.9.zip">
                    {{ $t('common.software.metasweeper') }} v3.1.9</a> {{ $t('common.software.download_link') }} 2<br>
                {{ $t('common.software.metasweeper_int') }}
            </li>
            <li><a style="color: blue;" target="_blank" href="https://fff666.top/download/Metaminesweeper-v3.1.11.zip">
                    {{ $t('common.software.metasweeper') }} v3.1.11</a> {{ $t('common.software.download_link') }} 1<br>
                <a style="color: blue;" target="_blank"
                    href="https://github.com/eee555/Solvable-Minesweeper/releases/download/3.1.11/Metaminesweeper-v3.1.11.zip">
                    {{ $t('common.software.metasweeper') }} v3.1.11</a> {{ $t('common.software.download_link') }} 2<br>
                {{ $t('common.software.metasweeper_int2') }}
            </li>
            <li><a style="color: blue;" target="_blank" href="https://fff666.top/download/Arbiter_0.52.3.zip">Arbiter
                    v0.52.3</a><br>
                {{ $t('common.software.arbiter_int') }}
            </li>

        </ul>

        <!-- <template #footer>
            <span class="dialog-footer">
                <el-button type="primary" @click="centerDialogVisible = false">
                    确定
                </el-button>
            </span>
        </template> -->
    </el-dialog>
</template>

<script lang="ts" setup>
// 注册、登录的弹框及右上方按钮
import { onMounted, ref, Ref } from 'vue'

import { useI18n } from 'vue-i18n';
const t = useI18n();

const centerDialogVisible = ref(false);



onMounted(() => {


})







</script>


<style></style>
