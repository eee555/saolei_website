<template>
    <ElDivider />
    <ElFooter>
        <ElRow style="margin-bottom: 15px">
            <ElCol :span="8">
                <div style="padding-bottom: 5px">
                    <strong>
                        {{ t('local.about') }}
                    </strong>
                </div>
                <BaseOverlay>
                    {{ t('local.team') }}
                    <template #header>
                        {{ t('local.team') }}
                    </template>
                    <template #overlay>
                        <Thanks />
                    </template>
                </BaseOverlay>
                <br>
                <Downloads />
            </ElCol>
            <ElCol :span="8">
                <div style="padding-bottom: 5px">
                    <strong>{{ t('local.contact') }}</strong>
                </div>
                <div>
                    <ElLink href="https://github.com/eee555/saolei_website" target="_blank" rel="noopener noreferrer">
                        GitHub
                    </ElLink>
                </div>
                <div>
                    <ElLink href="https://gitee.com/ee55/saolei_website" target="_blank" rel="noopener noreferrer">
                        Gitee
                    </ElLink>
                </div>
                <div>
                    <ElLink href="https://discord.gg/ks8ngPX5bT" target="_blank" rel="noopener noreferrer">
                        Discord
                    </ElLink>
                </div>
                <div>
                    <ElLink href="https://qm.qq.com/q/hNShGUQkJG" target="_blank" rel="noopener noreferrer">
                        QQ
                    </ElLink>
                </div>
            </ElCol>
            <ElCol :span="8">
                <div style="padding-bottom: 5px">
                    <strong>{{ t('local.links') }}</strong>
                </div>
                <div>
                    <ElLink href="http://saolei.wang" target="_blank" rel="noopener noreferrer">
                        扫雷网 saolei.wang
                    </ElLink>
                </div>
                <div>
                    <ElLink href="https://minesweepergame.com" target="_blank" rel="noopener noreferrer">
                        Authoritative Minesweeper
                    </ElLink>
                </div>
                <div>
                    <ElLink href="https://minesweeper.online" target="_blank" rel="noopener noreferrer">
                        Minesweeper.Online
                    </ElLink>
                </div>
                <div>
                    <ElLink href="http://tapsss.com" target="_blank" rel="noopener noreferrer">
                        扫雷联萌 League of Minesweeper
                    </ElLink>
                </div>
                <div>
                    <ElLink href="https://scoreganizer.net" target="_blank" rel="noopener noreferrer">
                        Scoreganizer
                    </ElLink>
                </div>
            </ElCol>
        </ElRow>
        <div style="text-align: center">
            <span class="text">
                Copyright @ 2023
            </span>
            <ElLink href="http://openms.top">
                开源扫雷网 openms.top
            </ElLink>
            <span class="text">
                　版权所有
            </span>
            <ElLink href="https://beian.miit.gov.cn/">
                苏ICP备2023056839号-1
            </ElLink>
            <span style="width: 12px; display: inline-block" />
            <ElLink
                href="https://beian.mps.gov.cn/#/query/webSearch?code=32020602001691" rel="noopener noreferrer"
                target="_blank"
            >
                苏公网安备32020602001691
            </ElLink>
        </div>
    </ElFooter>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ElCol, ElDivider, ElFooter, ElLink, ElRow } from 'element-plus';
import { useI18n } from 'vue-i18n';

import BaseOverlay from './common/BaseOverlay.vue';
import Downloads from './dialogs/Downloads.vue';
import Thanks from './dialogs/Thanks.vue';

/* 本地化 Localization */
const i18nMessage = {
    'zh-cn': { local: {
        contact: '联系我们',
        donate: '捐赠',
        team: '团队',
        links: '友链',
        about: '关于我们',
    } },
    en: { local: {
        contact: 'Contact',
        donate: 'Donate',
        team: 'Team',
        links: 'Links',
        about: 'About',
    } },
};

const { t } = useI18n({ messages: i18nMessage });
</script>
