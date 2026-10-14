<template>
    <div>
        {{ t('local.line1') }}
    </div>
    <div>
        {{ t('local.line2') }}
    </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const i18nMessages = {
    'zh-cn': { local: {
        line1: '在比赛期间任选2小时参赛。参赛后2小时区间内上传（以服务器接收时间为准）的所有录像中，取成绩最好的5局中级、2局高级，计算总成绩。',
        line2: '局数不够的，中级按照60秒，高级按照240秒补全。',
    } },
    en: { local: {
        line1: 'Choose any 2-hour interval during the tournament. Among all videos uploaded within (depending on when the server receives the file) 2 hours after the registration, sum up the best 5 intermediate games and 2 expert games.',
        line2: 'The default scores are 60s for intermediate and 240s for expert, when there are not enough games uploaded.',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>
