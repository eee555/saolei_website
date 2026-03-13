<template>
    <PrColumn field="end_time" :sortable="sortable" :header="t('common.prop.end_time')">
        <template #body="{ data }">
            <el-text>
                {{ utc_to_local_format(data.end_time) }}
            </el-text>
        </template>
    </PrColumn>
</template>

<script setup lang="ts">

import { ElText } from 'element-plus';
import PrColumn from 'primevue/column';
import { useI18n } from 'vue-i18n';

import { utc_to_local_format } from '@/utils/system/tools';

const { t } = useI18n();

defineProps({
    sortable: { type: Boolean, default: false },
});

</script>
