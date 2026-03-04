<template>
    <base-button-back @click="$emit('back')" />
    <el-button :disabled="importing || importingAll" @click="refresh">
        刷新
    </el-button>
    <el-button :disabled="importing || importingAll" @click="runImportSelected">
        导入选中
    </el-button>
    <el-button v-if="importingAll" :disabled="stopping" @click="stopping = true">
        停止导入
    </el-button>
    <DataTable
        v-model:filters="filters" v-model:selection="selectedData"
        v-loading="importingAll"
        element-loading-background="rgba(122, 122, 122, 0.4)"
        :value="tableData" row-hover size="small"
        sort-field="upload_time" :sort-order="-1"
        paginator :rows="10" :rows-per-page-options="[5, 10, 25, 50, 100]"
        :filter-button-props="{
            filter: {
                severity: 'secondary',
                text: true,
                rounded: false,
                size: 'small',
                style: { borderRadius: '0', padding: '0', width: '1rem' }
            }
        }"
        filter-display="menu" @row-click="handleRowClick"
    >
        <PrColumn selection-mode="multiple" header-style="width: 3rem" />
        <PrColumn field="upload_time" sortable :header="t('common.prop.upload_time')" style="min-width: 11em">
            <template #body="{ data }">
                <el-text>
                    {{ utc_to_local_format(data.upload_time) }}
                </el-text>
            </template>
        </PrColumn>
        <PrColumn field="level" :show-filter-match-modes="false" :show-filter-operator="false" style="width: 5em" :filter-header-style="{ marginInlineStart: '0px' }">
            <template #body="{ data }">
                <GameLevelIcon :level="data.level" />
            </template>
            <template #filter="{ filterModel, applyFilter }">
                <PrListbox v-model="filterModel.value" :options="[...MS_Levels]" @change="applyFilter()">
                    <template #option="slotProps">
                        <GameLevelIcon :level="slotProps.option" />
                    </template>
                </PrListbox>
            </template>
        </PrColumn>
        <PrColumn field="timems" :header="t('common.prop.time')" sortable>
            <template #body="{ data }: { data: SaoleiVideo }">
                {{ (data.timems / 1000).toFixed(2) }}
                <el-text v-if="data.nf" type="warning">
                    NF
                </el-text>
            </template>
        </PrColumn>
        <PrColumn field="bv" :header="t('common.prop.bv')" sortable />
        <PrColumn field="import_state" :header="t('common.prop.state')" :show-filter-match-modes="false" :show-filter-operator="false" :show-apply-button="false" :show-clear-button="false" :filter-header-style="{ marginInlineStart: '0px' }">
            <template #body="{ data }: { data: SaoleiVideo }">
                <SaoleiVideoStateIcon :state="data.import_state" />
            </template>
            <template #filter="{ filterModel, filterCallback }">
                <PrListbox v-model="filterModel.value" :options="Object.values(SaoleiVideoImportState)" @change="filterCallback()">
                    <template #option="slotProps">
                        <SaoleiVideoStateIcon :state="slotProps.option" />
                    </template>
                </PrListbox>
            </template>
        </PrColumn>
    </DataTable>
</template>

<script setup lang="ts">
import { FilterMatchMode } from '@primevue/core/api';
import { ElButton, ElText, vLoading } from 'element-plus';
import { DataTable } from 'primevue';
import PrColumn from 'primevue/column';
import PrListbox from 'primevue/listbox';
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import SaoleiVideoStateIcon from './SaoleiVideoStateIcon.vue';
import { SaoleiVideo, SaoleiVideoImportState } from './utils';

import BaseButtonBack from '@/components/common/BaseButtonBack.vue';
import { generalErrorNotification, httpErrorNotification, successNotification, unknownErrorNotification } from '@/components/Notifications';
import GameLevelIcon from '@/components/widgets/GameLevelIcon.vue';
import { preview } from '@/utils/common/PlayerDialog';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { MS_Levels } from '@/utils/ms_const';
import { utc_to_local_format } from '@/utils/system/tools';


const filters = ref({
    'import_state': { value: Object.values(SaoleiVideoImportState), matchMode: FilterMatchMode.IN },
    'level': { value: null, matchMode: FilterMatchMode.EQUALS },
});

const { proxy } = useCurrentInstance();
const { t } = useI18n();

const tableData = ref<SaoleiVideo[]>([]);
const selectedData = ref<SaoleiVideo[]>([]);
const importing = ref(false);
const importingAll = ref(false); // 指示runImportAll运行状态
const stopping = ref(false); // 控制runImportAll

const props = defineProps({
    saoleiId: {
        type: Number,
        required: true,
    },
});

function refresh() {
    tableData.value.splice(0, tableData.value.length);
    if (!props.saoleiId) return;
    proxy.$axios.get('accountlink/saolei/getlist/', {
        params: {
            saolei_id: props.saoleiId,
        },
    }).then((response) => {
        tableData.value = response.data;
    }).catch(httpErrorNotification);
}

watch(() => props.saoleiId, refresh, { immediate: true });

async function runImport(video: SaoleiVideo) {
    importing.value = true;
    video.import_state = SaoleiVideoImportState.IMPORTING;
    await proxy.$axios.post('accountlink/saolei/importvideo/', {
        video_id: video.id,
    }).then((response) => {
        const data = response.data;
        switch (data.type) {
            case 'success':
                Object.assign(video, data.data);
                successNotification(response);
                return;
            case 'error':
                video.import_state = SaoleiVideoImportState.FAILED;
                generalErrorNotification(data.object, data.category);
                return;
            default:
                unknownErrorNotification(data);
                return;
        }
    }).catch(httpErrorNotification);
    importing.value = false;
}

async function runImportSelected() {
    importingAll.value = true;
    for (const video of selectedData.value) {
        if (stopping.value) break;
        if (video.import_state !== SaoleiVideoImportState.IMPORTED && video.import_state !== SaoleiVideoImportState.IMPORTING) {
            await runImport(video);
        }
    }
    importingAll.value = false;
}

function handleRowClick(event: any) {
    if (event.data.import_state === SaoleiVideoImportState.IMPORTING) {
        return;
    } else if (event.data.import_state === SaoleiVideoImportState.IMPORTED) {
        preview(event.data.import_video);
    } else {
        runImport(event.data);
    }
}

defineEmits(['back']);
</script>

<style lang="less" scoped>
.el-overlay .p-select-overlay {
    z-index: 3000 !important;
}

</style>
