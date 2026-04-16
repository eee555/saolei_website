<template>
    <div class="text text-medium">
        <ul>
            <li>
                {{ t('local.line_1') }}
            </li>
            <li>
                {{ t('local.line_2') }}
            </li>
            <li>
                {{ t('local.line_3') }}
            </li>
            <li>
                {{ t('local.line_4') }}
            </li>
        </ul>
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import { useI18n } from 'vue-i18n';

const i18nMessages = {
    'zh-cn': { local: {
        line_1: '录像同步功能代替您从扫雷网下载录像并上传到开源扫雷网。更进一步地，开源扫雷网采信扫雷网上显示的上传时间。如果您在两个网站上传了重复的录像，开源扫雷网将采用更早的上传时间。',
        line_2: '录像同步分为两个子功能：收藏与导入。“收藏”会访问您的个人主页，收集所有录像的元数据，包括录像id、上传时间等。“导入”则直接通过录像id下载录像并通过开源扫雷网的审核流程。',
        line_3: '收藏和导入均在后台运行，运行中网页会每30秒刷新一次进度。',
        line_4: '刷新收藏有两种模式。增量模式遇到已经收藏过的录像就停止，全量模式会一直扫描到最后一页。',
    } },
    'en': { local: {
        line_1: "The function of video synchronization helps you download videos from @:common.website.saolei and upload them to @:{'common.website.openms'}. Furthermore, @:{'common.website.openms'} will respect the upload time provided by @:{'common.website.saolei'}. If you have uploaded the same file to both websites, @:{'common.website.openms'} will take the earlier upload time.", // eslint-disable-line @stylistic/quotes
        line_2: "There are two sub-functions: collecting and importing. The collecting will visit your profile and gather the metadata of all videos, including video ID and upload time. The importing will access the video file through video ID and pass the file through @:{'common.website.openms'}'s verification process.", // eslint-disable-line @stylistic/quotes
        line_3: 'Both collecting and importing run in the background. The page will update their progress every 30 seconds.',
        line_4: 'The collecting has two modes. The "New" mode is cheaper: it stops at the first already-collected video. The "All" mode is more expensive: it scans all videos, even if they have been collected before.',
    } },
};

const { t } = useI18n({
    messages: i18nMessages,
});

</script>
