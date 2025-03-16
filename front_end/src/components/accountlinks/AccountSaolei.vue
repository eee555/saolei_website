<template>
    <el-descriptions border>
        <el-descriptions-item :label="t('common.prop.update_time')" :span="2">
            {{ utc_to_local_format(data.update_time) }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('accountlink.saoleiName')">
            {{ data.name }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('accountlink.saoleiTotalViews')">
            {{ data.total_views }}
        </el-descriptions-item>
    </el-descriptions>
    <el-table :data="datatable">
        <el-table-column prop="category" />
        <el-table-column prop="b" :label="t('common.level.b')" />
        <el-table-column prop="i" :label="t('common.level.i')" />
        <el-table-column prop="e" :label="t('common.level.e')" />
        <el-table-column prop="s" :label="t('common.level.sum')" />
    </el-table>
</template>

<script setup lang="ts">
import { cs_to_s, ms_to_s } from '@/utils';
import { utc_to_local_format } from '@/utils/system/tools';
import { computed, PropType } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElDescriptions, ElDescriptionsItem, ElTable, ElTableColumn} from 'element-plus';

const prop = defineProps({
    data: {
        type: Object as PropType<any>,
        default() { return {}; },
    }
})

const { t } = useI18n()

const datatable = computed(() => [
    {category: t('common.prop.time'), b: ms_to_s(prop.data.b_t_ms), i: ms_to_s(prop.data.i_t_ms), e: ms_to_s(prop.data.e_t_ms), s: ms_to_s(prop.data.b_t_ms+prop.data.i_t_ms+prop.data.e_t_ms)},
    {category: t('common.prop.bvs'), b: cs_to_s(prop.data.b_b_cent), i: cs_to_s(prop.data.i_b_cent), e: cs_to_s(prop.data.e_b_cent), s: cs_to_s(prop.data.b_b_cent+prop.data.i_b_cent+prop.data.e_b_cent)},
    {category: t('accountlink.saoleiVideoCount'), b: prop.data.beg_count, i: prop.data.int_count, e: prop.data.exp_count, s: prop.data.beg_count+prop.data.int_count+prop.data.exp_count}
])

</script>