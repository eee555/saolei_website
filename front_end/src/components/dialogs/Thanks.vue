<template>
    <div style="padding-bottom: 5px">
        <strong>{{ t('local.owner') }}</strong>
    </div>
    <div>
        <GitHubUser username="eee555" />
    </div>
    <div style="padding-bottom: 5px; margin-top: 15px">
        <strong>{{ t('local.moderator') }}</strong>
    </div>
    <div>少年</div>
    <div>GodnuX</div>
    <div>auk ;-;</div>
    <el-divider />
    <el-row>
        <el-col :span="8">
            <div style="padding-bottom: 5px">
                <strong>{{ t('local.software') }}</strong>
            </div>
            <div>
                <GitHubUser username="eee555" />
            </div>
            <div>
                <GitHubUser username="putianyi889" />
            </div>
            <div>
                <GitHubUser username="ljzloser" />
            </div>
            <div>
                <GitHubUser username="hwatson381" />
            </div>
            <div>
                <GitHubUser username="hgraceb" />
            </div>
        </el-col>
        <el-col :span="8">
            <div style="padding-bottom: 5px">
                <strong>{{ t('local.localization') }}</strong>
            </div>
            <div>
                {{ t('local.zhCn') }}
                <GitHubUser username="putianyi889" />
            </div>
            <div>
                {{ t('local.en') }}
                <GitHubUser username="putianyi889" />
            </div>
            <div>
                {{ t('local.de') }}
                <GitHubUser username="auk3" />
            </div>
            <div>
                {{ t('local.pl') }}
                <GitHubUser username="kiraa96" />
            </div>
        </el-col>
        <el-col :span="8">
            <div style="padding-bottom: 5px">
                <strong>{{ t('local.designer') }}</strong>
            </div>
            <div>
                <GitHubUser username="eee555" />
            </div>
            <div>
                <GitHubUser username="putianyi889" />
            </div>
        </el-col>
    </el-row>
    <el-divider />
    <div style="padding-bottom: 5px">
        <strong>{{ t('local.acknowledgement') }}</strong>
    </div>
    <span v-for="item in acknowledgements" style="padding-right: 10px">
        {{ item.text }}
    </span>
</template>

<script lang="ts" setup>
// 注册、登录的弹框及右上方按钮
import { ElCol, ElDivider, ElRow } from 'element-plus';
import { useI18n } from 'vue-i18n';

import GitHubUser from '@/components/widgets/GitHubUser.vue';

// 积分系统完成后需要加jsd
const acknowledgements = [
    { text: 'T0nyX1ang' },
    { text: 'Pulsar' },
    { text: 'darkness' },
    { text: 'lc4337' },
    { text: '冰糖雪梨' },
    { text: '生命★是┗ 〓┛是☆什么' },
    { text: 'Arya' },
];

/* 本地化 Localization */
const i18nMessage = {
    'zh-cn': { local: {
        owner: '站长',
        moderator: '管理员',
        software: '开发',
        localization: '本地化',
        zhCn: '简体中文',
        en: '英语',
        de: '德语',
        pl: '波兰语',
        designer: '外观设计',
        acknowledgement: '致谢',
    } },
    'en': { local: {
        owner: 'Owner',
        moderator: 'Moderators',
        software: 'Developers',
        localization: 'Localization',
        zhCn: 'Simplified Chinese',
        en: 'English',
        de: 'German',
        pl: 'Polish',
        designer: 'UI designers',
        acknowledgement: 'Acknowledgement',
    } },
};

const { t } = useI18n({ messages: i18nMessage });
</script>
