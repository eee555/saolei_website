<template>
    <!-- <span class="text-button" @click="centerDialogVisible = true;"> -->
    <el-link @click="centerDialogVisible = true;">
        {{ t('common.software.software_download') }}
    </el-link>
    <el-dialog
        v-model="centerDialogVisible" :title="t('common.software.software_download')" width="50%" align-center
        draggable :lock-scroll="false"
    >
        <ul>
            <li>
                <a style="color: blue;" target="_blank" href="https://openms.top/download/Metaminesweeper-v3.1.9.zip">
                    {{ t('common.software.metasweeper') }} v3.1.9</a> {{ t('common.software.download_link') }} 1<br>
                <a
                    style="color: blue;" target="_blank"
                    href="https://github.com/eee555/Solvable-Minesweeper/releases/download/3.1.9/Metaminesweeper-v3.1.9.zip"
                >
                    {{ t('common.software.metasweeper') }} v3.1.9</a> {{ t('common.software.download_link') }} 2<br>
                {{ t('common.software.metasweeper_int') }}
            </li>
            <li>
                <a style="color: blue;" target="_blank" href="https://openms.top/download/Metaminesweeper-v3.1.11.zip">
                    {{ t('common.software.metasweeper') }} v3.1.11</a> {{ t('common.software.download_link') }} 1<br>
                <a
                    style="color: blue;" target="_blank"
                    href="https://github.com/eee555/Solvable-Minesweeper/releases/download/3.1.11/Metaminesweeper-v3.1.11.zip"
                >
                    {{ t('common.software.metasweeper') }} v3.1.11</a> {{ t('common.software.download_link') }} 2<br>
                {{ t('common.software.metasweeper_int2') }}
            </li>
            <li>
                <a style="color: blue;" target="_blank" href="https://gitee.com/ee55/Metasweeper/releases/download/3.2.0/Metaminesweeper-3.2.0.exe">
                    {{ t('common.software.metasweeper') }} v3.2.0</a> {{ t('common.software.download_link') }} 1<br>
                <a
                    style="color: blue;" target="_blank"
                    href="https://github.com/eee555/Metasweeper/releases/download/3.2.0/Metaminesweeper-3.2.0.exe"
                >
                    {{ t('common.software.metasweeper') }} v3.2.0</a> {{ t('common.software.download_link') }} 2<br>
                {{ t('common.software.metasweeper_int2') }}
            </li>
            <li>
                <a style="color: blue;" target="_blank" href="https://openms.top/download/Arbiter_0.52.3.zip">Arbiter
                    v0.52.3</a><br>
                {{ t('common.software.arbiter_int') }}
            </li>
        </ul>
    </el-dialog>
</template>

<script lang="ts" setup>
// 注册、登录的弹框及右上方按钮
import { ElDialog, ElLink } from 'element-plus';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const centerDialogVisible = ref(false);

</script>
