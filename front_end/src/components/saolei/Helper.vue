<template>
    <el-text size="large">
        <ul>
            <li>使用本工具之前，请确保您已经正确关联了扫雷网账号，并且已经在开源扫雷网实名。</li>
            <li>
                本工具代替用户上传已经上传至扫雷网的录像。服务器会分两步获取用户的录像文件：
                <ol>
                    <li>访问用户的地盘，以页为单位（页码从1开始，每页22个录像）从“最新录像”获取用户的录像基本信息，包括录像id、上传时间、级别、用时、bv、NF，将信息存入导入队列等待操作。</li>
                    <li>从导入队列中取出一条录像信息，通过录像id访问该录像页，获取录像文件的下载链接。通过下载链接下载录像源文件，视为用户上传了该录像，进行正常的上传流程。如果该录像在开源扫雷网已经存在了，则比对该录像在扫雷网和开源扫雷网的上传时间，以较早的为准。</li>
                </ol>
                这两步独立通过API控制。“一键导入”功能会使用脚本自动操作。“导入队列”允许用户控制第二步。用户理论上可以自行编写脚本实现这两步操作。
            </li>
            <li>相比于用户手动上传，本工具保留了上传时间信息（精确到分）。</li>
            <li>通过本工具导入录像时，不会检查用户的录像数量。如果导入的录像超过了用户的录像数量限制，虽然可以正常导入，但是用户会因为录像超额而无法通过开源扫雷网上传新录像。</li>
        </ul>
    </el-text>
    <el-row justify="center">
        <el-button size="large" @click="$emit('back')">
            返回菜单
        </el-button>
        <el-button size="large" @click="$emit('enterAuto')">
            一键导入
        </el-button>
        <el-button size="large" @click="$emit('enterQueue')">
            导入队列
        </el-button>
    </el-row>
</template>

<script setup lang="ts">
import { ElButton, ElRow, ElText } from 'element-plus';

defineEmits(['back', 'enterAuto', 'enterQueue']);
</script>
