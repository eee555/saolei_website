<template>
    <PrDataTable
        v-model:filters="filters"
        v-loading="importing"
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
        filter-display="menu"
    >
        <PrColumn field="id" sortable header="ID" />
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
        <PrColumn field="import_task__status" :header="t('common.prop.state')" :show-filter-match-modes="false" :show-filter-operator="false" :show-apply-button="false" :show-clear-button="false" :filter-header-style="{ marginInlineStart: '0px' }">
            <template #body="{ data }: { data: SaoleiVideo }">
                <el-text v-if="data.import_task__status == 'RUNNING'" type="warning">
                    {{ t('accountlink.importStatus.running') }}
                </el-text>
                <el-text v-else-if="data.import_task__status == 'SUCCESSFUL' && data.import_video__id != 0" type="success">
                    {{ t('accountlink.importStatus.successful') }}（新）
                </el-text>
                <el-text v-else-if="data.import_task__status == 'FAILED'" type="danger">
                    {{ t('accountlink.importStatus.failed') }}
                </el-text>
                <el-text v-else-if="data.import_task__status == 'READY'" type="primary">
                    {{ t('accountlink.importStatus.ready') }}
                </el-text>
                <el-text v-else-if="data.import_task__status == 'SUCCESSFUL' && data.import_video__id == 0" type="danger">
                    {{ t('accountlink.importStatus.connection') }}
                </el-text>
                <el-text v-else-if="data.import_task__status == 'NULL' && data.import_video__id != 0" type="success">
                    {{ t('accountlink.importStatus.successful') }}
                </el-text>
            </template>
            <template #filter="{ filterModel, filterCallback }">
                <PrListbox v-model="filterModel.value" :options="[...DjangoTaskResultStatusOptions]" @change="filterCallback()">
                    <template #option="slotProps">
                        <DjangoTaskResultStatusBadge :status="slotProps.option" />
                    </template>
                </PrListbox>
            </template>
        </PrColumn>
        <PrColumn>
            <template #body="{ data }: { data: SaoleiVideo }">
                <el-link v-if="data.import_video__id != 0" underline="never" @click="preview(data.import_video__id)">
                    <i class="pi pi-play-circle" />
                </el-link>
            </template>
        </PrColumn>
    </PrDataTable>
</template>

<script setup lang="ts">
import 'primeicons/primeicons.css';
import '@/styles/button.css';

import { FilterMatchMode } from '@primevue/core/api';
import { ElLink, ElText, vLoading } from 'element-plus';
import PrColumn from 'primevue/column';
import PrDataTable from 'primevue/datatable';
import PrListbox from 'primevue/listbox';
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { SaoleiVideo } from './utils';

import { httpErrorNotification } from '@/components/Notifications';
import DjangoTaskResultStatusBadge from '@/components/widgets/DjangoTaskResultStatusBadge.vue';
import GameLevelIcon from '@/components/widgets/GameLevelIcon.vue';
import { preview } from '@/utils/common/PlayerDialog';
import { DjangoTaskResultStatusOptions } from '@/utils/common/structInterface';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { MS_Levels } from '@/utils/ms_const';
import { utc_to_local_format } from '@/utils/system/tools';


const filters = ref({
    'import_task__status': { value: null, matchMode: FilterMatchMode.EQUALS },
    'level': { value: null, matchMode: FilterMatchMode.EQUALS },
});

const { proxy } = useCurrentInstance();
const { t } = useI18n();

const tableData = ref<SaoleiVideo[]>([]);
const importing = ref(false);

const props = defineProps({
    saoleiId: {
        type: Number,
        required: true,
    },
});

function refresh() {
    tableData.value.splice(0, tableData.value.length);
    if (!props.saoleiId) return;
    proxy.$axios.get('accountlink/saolei/videolist/get/', {
        params: {
            saolei_id: props.saoleiId,
        },
    }).then((response) => {
        tableData.value = preprocessTable(response.data);
    }).catch(httpErrorNotification);
}

watch(() => props.saoleiId, refresh, { immediate: true });

function preprocessTable(data: any) {
    data.forEach(((video: any) => {
        if (video.import_video__id === null) video.import_video__id = 0;
        if (video.import_task__status === null) video.import_task__status = 'NULL';
    }));
    return data;
}

defineEmits(['back', 'enterAuto', 'enterHelp']);
</script>

<style lang="less" scoped>
.el-overlay .p-select-overlay {
    z-index: 3000 !important;
}

</style>
