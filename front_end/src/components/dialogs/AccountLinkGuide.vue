<template>
    <span v-if="platform == 'c'" class="text">
        <b>{{ t('accountlink.guideTitle') }}</b><br>
        {{ t('accountlink.guideSaolei1') }}
        <PlatformIcon platform="c" />{{ t('accountlink.guideSaolei2') }}<br>
        <img src="../../assets/IdGuideSaolei.png" width="100%">
    </span>
    <span v-else-if="platform == 'a'" class="text">
        <b>{{ t('accountlink.guideTitle') }}</b><br>
        {{ t('accountlink.guideMsgames1') }}
        <PlatformIcon platform="a" />{{ t('accountlink.guideMsgames2') }}<br>
        <img src="../../assets/IdGuideMsgames1.png" width="100%">
        {{ t('accountlink.guideMsgames3') }}
        <img src="../../assets/IdGuideMsgames2.png" width="100%">
    </span>
    <span v-else-if="platform == 'w'" class="text">
        <b>{{ t('accountlink.guideTitle') }}</b><br>
        {{ t('accountlink.guideWom1') }}
        <PlatformIcon platform="w" />{{ t('accountlink.guideWom2') }}
        <img src="../../assets/IdGuideWom.png" width="100%">
    </span>
    <span v-else-if="platform == 'q'" class="text">
        {{ t('accountlink.guideQQ') }}
    </span>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import { useI18n } from 'vue-i18n';

import PlatformIcon from '@/components/widgets/PlatformIcon.vue';

const { t } = useI18n();

defineProps({
    platform: {
        type: String,
        default: '',
    },
});

</script>
