<template>
    <ElRow>
        <UserArbiterCSV :id="user.id" />
        <span style="flex: 1" />
        <ElButton circle :type="showSetting ? 'primary' : 'default'" @click="showSetting = !showSetting">
            <BaseIconSetting />
        </ElButton>
    </ElRow>
    <MultiSelector v-if="showSetting" v-model="VideoListConfig.profile" :options="thisColumnChoices" :labels="thisColumnChoices.map((s) => t(`common.prop.${s}`))" />
    <VideoList v-loading="loading" :videos="user.videos" :columns="VideoListConfig.profile" sortable paginator />
</template>

<script lang="ts" setup>
// 个人主页的个人所有录像部分
import { ElButton, ElRow, vLoading } from 'element-plus';
import { onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';


import { BaseIconSetting } from '@/components/common/icon';
import VideoList from '@/components/VideoList/App.vue';
import MultiSelector from '@/components/widgets/MultiSelector.vue';
import UserArbiterCSV from '@/components/widgets/UserArbiterCSV.vue';
import { fetchUserVideos } from '@/services/userService';
import { VideoListConfig } from '@/store';
import { ArrayUtils } from '@/utils/arrays';
import { ColumnChoices } from '@/utils/ms_const';
import { UserProfile } from '@/utils/userprofile';


const { t } = useI18n();

const user = defineModel('user', { type: UserProfile, required: true });

const showSetting = ref(false);
const thisColumnChoices = ArrayUtils.sortByReferenceOrder(['bv', 'bvs', 'stnb', 'ces', 'cls', 'corr', 'end_time', 'ioe', 'level', 'state', 'software', 'thrp', 'time', 'upload_time', 'path', 'file_size', 'mode'], ColumnChoices);

const loading = ref(false);

async function refresh() {
    if (loading.value) return;
    if (user.value.id < 1) return;
    if (user.value.videos === undefined) {
        loading.value = true;
        user.value.videos = await fetchUserVideos(user.value.id);
        loading.value = false;
    }
}

watch(() => user.value.id, refresh, { immediate: true });

onMounted(refresh);
</script>
