<template>
    <PrColumn field="upload_time" :sortable="sortable" :header="t('common.prop.upload_time')" style="min-width: 11em">
        <template #body="{ data }">
            <el-text>
                {{ utc_to_local_format(data.upload_time) }}
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
