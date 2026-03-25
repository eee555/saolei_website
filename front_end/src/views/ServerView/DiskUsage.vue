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
const { t } = useI18n();
const loading = ref(false);

const diskUsage = ref({
    total: 0,
    used: 0,
    free: 0,
    video: 0,
    db: 0,
});

const diskUsageData = computed(() => [
    { name: t('server.diskUsage.label.video'), values: [diskUsage.value.video] },
    { name: t('server.diskUsage.label.db'), values: [diskUsage.value.db] },
    { name: t('server.diskUsage.label.other'), values: [diskUsage.value.total - diskUsage.value.video - diskUsage.value.db] },
    { name: t('server.diskUsage.label.free'), values: [diskUsage.value.free] },
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
                    text: t('server.diskUsage.title'),
                },
            },
        },
    } as VueUiDonutConfig;
});

</script>
