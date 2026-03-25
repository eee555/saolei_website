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
const { t } = useI18n();
const dataset = ref<VueUiDonutDatasetItem[]>([]);
const loading = ref(false);

function refresh() {
    loading.value = true;
    proxy.$axios.get('/common/api/tasksummary').then((response) => {
        dataset.value = [
            {
                name: t('task.status.READY'),
                values: [response.data.READY],
            },
            {
                name: t('task.status.RUNNING'),
                values: [response.data.RUNNING],
            },
            {
                name: t('task.status.SUCCESSFUL'),
                values: [response.data.SUCCESSFUL],
            },
            {
                name: t('task.status.FAILED'),
                values: [response.data.FAILED],
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
                    text: t('task.title'),
                },
            },
        },
    } as VueUiDonutConfig;
});
</script>
