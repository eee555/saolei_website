<template>
    <PrColumn field="level" :show-filter-match-modes="false" :show-filter-operator="false" style="width: 5em" :filter-header-style="{ marginInlineStart: '0px' }">
        <template #body="{data}: {data: VideoAbstract}">
            <span v-if="data.isLocal && !isStandardLevel(data.level)">—</span>
            <GameLevelIcon v-else :level="data.level" />
        </template>
        <template #filter="{ filterModel, applyFilter }">
            <PrListbox v-model="filterModel.value" :options="[...MS_Levels]" @change="applyFilter()">
                <template #option="slotProps">
                    <GameLevelIcon :level="slotProps.option" />
                </template>
            </PrListbox>
        </template>
    </PrColumn>
</template>

<script setup lang="ts">
import PrColumn from 'primevue/column';
import PrListbox from 'primevue/listbox';

import GameLevelIcon from '@/components/widgets/GameLevelIcon.vue';
import { isStandardLevel, MS_Levels } from '@/utils/ms_const';
import type { VideoAbstract } from '@/utils/videoabstract';
</script>

<style lang="less">
.p-datatable-popover-filter {
    margin-inline-start: 0px;
}
</style>
