<template>
    <base-card-normal>
        <VueUiDonut :dataset="diskUsageData" :config="config" />
    </base-card-normal>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { VueUiDonut, VueUiDonutConfig } from 'vue-data-ui';
import { useI18n } from 'vue-i18n';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { local } from '@/store';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { formatBytes } from '@/utils/strings';


const { proxy } = useCurrentInstance();
const loading = ref(false);

const diskUsage = ref({
    total: 0,
    used: 0,
    free: 0,
    video: 0,
    db: 0,
});

const diskUsageData = computed(() => [
    { name: t('local.video'), values: [diskUsage.value.video] },
    { name: t('local.db'), values: [diskUsage.value.db] },
    { name: t('local.other'), values: [diskUsage.value.total - diskUsage.value.video - diskUsage.value.db] },
    { name: t('local.free'), values: [diskUsage.value.free] },
]);

async function refresh() {
    loading.value = true;
    await proxy.$axios.get('/common/api/diskusage').then(function (response) {
        const data = response.data as {
            total: number;
            used: number;
            free: number;
            video: number;
            db: number;
        };
        Object.assign(diskUsage.value, data);
        loading.value = false;
    });
}

onMounted(refresh);

const config = computed(() => {
    return {
        loading: loading.value,
        theme: local.value.darkmode ? 'dark' : '',
        style: {
            chart: {
                layout: {
                    labels: {
                        value: {
                            formatter: ({ value }) => formatBytes(value, 1),
                        },
                        hollow: {
                            average: {
                                show: false,
                            },
                            total: {
                                text: t('common.score.total'),
                                value: {
                                    formatter: ({ value }) => formatBytes(value, 1),
                                },
                            },
                        },
                    },
                },
                title: {
                    text: t('local.title'),
                },
            },
        },
    } as VueUiDonutConfig;
});


const i18nMessages = {
    'zh-cn': { local: {
        title: '磁盘使用情况',
        video: '录像文件',
        db: '数据库',
        other: '其他文件',
        free: '可用空间',
    } },
    'en': { local: {
        title: 'Disk Usage',
        video: 'Videos',
        db: 'Database',
        other: 'Other',
        free: 'Free',
    } },
};

const { t } = useI18n({
    messages: i18nMessages,
});

</script>
