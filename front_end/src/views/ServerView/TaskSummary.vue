<template>
    <base-card-normal style="max-width: 40em">
        <vue-ui-donut :dataset="dataset" :config="config" />
    </base-card-normal>
</template>

<script setup lang="ts">
import 'vue-data-ui/style.css';
import { computed, onMounted, ref } from 'vue';
import { VueUiDonut, VueUiDonutConfig, VueUiDonutDatasetItem } from 'vue-data-ui';
import { useI18n } from 'vue-i18n';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import { local } from '@/store';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const { proxy } = useCurrentInstance();
const dataset = ref<VueUiDonutDatasetItem[]>([]);
const loading = ref(false);

function refresh() {
    loading.value = true;
    proxy.$axios.get('/common/api/tasksummary').then((response) => {
        dataset.value = [
            {
                name: t('local.READY'),
                values: [response.data.status.READY],
            },
            {
                name: t('local.RUNNING'),
                values: [response.data.status.RUNNING],
            },
            {
                name: t('local.SUCCESSFUL'),
                values: [response.data.status.SUCCESSFUL],
            },
            {
                name: t('local.FAILED'),
                values: [response.data.status.FAILED],
            },
        ];
    });
    loading.value = false;
}

onMounted(refresh);

const config = computed<VueUiDonutConfig>(() => {
    return {
        loading: loading.value,
        theme: local.value.darkmode ? 'dark' : '',
        style: {
            chart: {
                layout: {
                    labels: {
                        hollow: {
                            average: {
                                show: false,
                            },
                            total: {
                                text: t('common.score.total'),
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

/* 本地化 Localization */
const i18nMessages = {
    'zh-cn': { local: {
        title: '后台任务',
        READY: '排队中',
        RUNNING: '运行中',
        SUCCESSFUL: '已完成',
        FAILED: '失败',
    } },
    'en': { local: {
        title: 'Background tasks',
        READY: 'Ready',
        RUNNING: 'Running',
        SUCCESSFUL: 'Successful',
        FAILED: 'Failed',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>
