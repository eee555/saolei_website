<template>
    <el-divider />
    <el-footer>
        <el-row style="margin-bottom: 15px">
            <el-col :span="8">
                <div style="padding-bottom: 5px">
                    <strong>
                        {{ t('footer.about') }}
                    </strong>
                </div>
                <Thanks />
                <!-- <div><el-link href="https://github.com/eee555/Solvable-Minesweeper">{{ $t('common.software.metasweeper')
                        }}</el-link></div> -->
                <div style="padding-bottom: 5px; margin-top: 8px;">
                    <strong>
                        {{ t('common.software.resource_download') }}
                    </strong>
                </div>
                <Downloads />
            </el-col>
            <el-col :span="8">
                <div style="padding-bottom: 5px">
                    <strong>{{ t('footer.contact') }}</strong>
                </div>
                <div>
                    <el-link href="https://github.com/eee555/saolei_website" target="_blank">
                        GitHub
                    </el-link>
                </div>
                <div>
                    <el-link href="https://gitee.com/ee55/saolei_website" target="_blank">
                        Gitee
                    </el-link>
                </div>
                <div>
                    <el-link href="https://discord.gg/ks8ngPX5bT" target="_blank">
                        Discord
                    </el-link>
                </div>
                <div>
                    <el-link href="https://qm.qq.com/q/hNShGUQkJG" target="_blank">
                        QQ
                    </el-link>
                </div>
            </el-col>
            <el-col :span="8">
                <div style="padding-bottom: 5px">
                    <strong>{{ t('footer.links') }}</strong>
                </div>
                <div>
                    <el-link href="http://saolei.wang" target="_blank">
                        扫雷网 saolei.wang
                    </el-link>
                </div>
                <div>
                    <el-link href="https://minesweepergame.com" target="_blank">
                        Authoritative Minesweeper
                    </el-link>
                </div>
                <div>
                    <el-link href="https://minesweeper.online" target="_blank">
                        Minesweeper.Online
                    </el-link>
                </div>
                <div>
                    <el-link href="http://tapsss.com" target="_blank">
                        扫雷联萌 League of Minesweeper
                    </el-link>
                </div>
                <div>
                    <el-link href="https://scoreganizer.net" target="_blank">
                        Scoreganizer
                    </el-link>
                </div>
            </el-col>
        </el-row>
        <div style="text-align: center">
            <el-text style="vertical-align: middle">
                Copyright @ 2023
            </el-text>
            <el-link href="http://openms.top">
                开源扫雷网 openms.top
            </el-link>
            <el-text style="vertical-align: middle">
                　版权所有
            </el-text>
            <el-link href="https://beian.miit.gov.cn/">
                苏ICP备2023056839号-1
            </el-link>
            <span style="width: 12px; display: inline-block" />
            <el-link
                href="https://beian.mps.gov.cn/#/query/webSearch?code=32020602001691" rel="noreferrer"
                target="_blank"
            >
                苏公网安备32020602001691
            </el-link>
        </div>
    </el-footer>
</template>

<script setup lang="ts">
import { ElCol, ElDivider, ElFooter, ElLink, ElRow, ElText } from 'element-plus';
import { useI18n } from 'vue-i18n';

import Downloads from './dialogs/Downloads.vue';
import Thanks from './dialogs/Thanks.vue';

const { t } = useI18n();

</script>
