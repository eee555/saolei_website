<template>
    <span v-if="platform == 'c'" class="text">
        <b>{{ t('local.title') }}</b><br>
        {{ t('local.saolei1') }}
        <PlatformIcon platform="c" />{{ t('local.saolei2') }}<br>
        <img src="../../assets/IdGuideSaolei.png" width="100%">
    </span>
    <span v-else-if="platform == 'a'" class="text">
        <b>{{ t('local.title') }}</b><br>
        {{ t('local.msgames1') }}
        <PlatformIcon platform="a" />{{ t('local.msgames2') }}<br>
        <img src="../../assets/IdGuideMsgames1.png" width="100%">
        {{ t('local.msgames3') }}
        <img src="../../assets/IdGuideMsgames2.png" width="100%">
    </span>
    <span v-else-if="platform == 'w'" class="text">
        <b>{{ t('local.title') }}</b><br>
        {{ t('local.wom1') }}
        <PlatformIcon platform="w" />{{ t('local.wom2') }}
        <img src="../../assets/IdGuideWom.png" width="100%">
    </span>
    <span v-else-if="platform == 'q'" class="text">
        {{ t('local.QQ') }}
    </span>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import { useI18n } from 'vue-i18n';

import PlatformIcon from '@/components/widgets/PlatformIcon.vue';


defineProps({
    platform: {
        type: String,
        default: '',
    },
});


const i18nMessages = {
    'zh-cn': { local: {
        msgames1: '在',
        msgames2: '排行榜找到你的位置：',
        msgames3: '在上图点击名字右边的链接，进入如下的个人主页，网址结尾的数字就是ID。',
        QQ: 'QQ号信息网站管理员可见。请注意隐私安全。',
        saolei1: '登录',
        saolei2: '，进入“我的地盘”，ID位置如下图所示。',
        title: '如何找到ID',
        wom1: '在',
        wom2: '进入你的个人主页，网址结尾的数字就是你的ID。',
    } },
    'en': { local: {
        msgames1: 'Find yourself on the ',
        msgames2: ' ranking:',
        msgames3: 'Click the link next to your name (see image above) to get to your profile (see image below). The number at the end of the url is your ID.',
        QQ: 'The QQ number is accessible from site moderators. Please be aware of your privacy safety.',
        saolei1: 'Go to your profile page on ',
        saolei2: '. The positions of the ID are shown below.',
        title: 'How to locate the ID',
        wom1: 'Go to your profile page on ',
        wom2: '. The number at the end of the url is your ID.',
    } },
};

const { t } = useI18n({
    messages: i18nMessages,
});

</script>
