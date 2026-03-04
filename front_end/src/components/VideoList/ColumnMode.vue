<template>
    <PrColumn field="mode" :show-filter-match-modes="false" :show-filter-operator="false" style="width: 5em">
        <template #body="{ data }">
            <el-text>
                {{ t(`common.mode.code${data.mode}`) }}
            </el-text>
        </template>
        <template #filter="{ filterModel, filterCallback }">
            <PrListbox v-model="filterModel.value" :options="Object.values(MS_Mode)" multiple @change="filterCallback()">
                <template #option="slotProps">
                    {{ t(`common.mode.code${slotProps.option}`) }}
                </template>
            </PrListbox>
        </template>
    </PrColumn>
</template>

<script setup lang="ts">

import { ElText } from 'element-plus';
import PrColumn from 'primevue/column';
import PrListbox from 'primevue/listbox';
import { useI18n } from 'vue-i18n';

import { MS_Mode } from '@/utils/ms_const';

const { t } = useI18n();

</script>
