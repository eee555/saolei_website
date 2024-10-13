<template>
    <el-text v-if="platform == 'c'">
        <b>{{ $t('accountlink.guideTitle') }}</b><br />
        {{ $t('accountlink.guideSaolei1') }}
        <PlatformIcon platform="c" />{{ $t('accountlink.guideSaolei2') }}<br />
        <img src="../../assets/IdGuideSaolei.png" width="100%" />
    </el-text>
    <el-text v-else-if="platform == 'a'">
        <b>{{ $t('accountlink.guideTitle') }}</b><br />
        {{ $t('accountlink.guideMsgames1') }}
        <PlatformIcon platform="a" />{{ $t('accountlink.guideMsgames2') }}<br />
        <img src="../../assets/IdGuideMsGames1.png" width="100%" />
        {{ $t('accountlink.guideMsgames3') }}
        <img src="../../assets/IdGuideMsGames2.png" width="100%" />
    </el-text>
    <el-text v-else-if="platform == 'w'">
        <b>{{ $t('accountlink.guideTitle') }}</b><br />
        {{ $t('accountlink.guideWom1') }}
        <PlatformIcon platform="w" />{{ $t('accountlink.guideWom2') }}
        <img src="../../assets/IdGuideWom.png" width="100%" />
    </el-text>
</template>

<script setup lang="ts">

import PlatformIcon from "@/components/widgets/PlatformIcon.vue"

const data = defineProps({
    platform: {
        type: String,
        default: "",
    },
});

</script>