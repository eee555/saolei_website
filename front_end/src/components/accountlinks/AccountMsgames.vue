<template>
    <el-descriptions border>
        <el-descriptions-item :label="t('common.prop.update_time')" :span="2">
            {{ utc_to_local_format(data.update_time) }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('accountlink.msgamesName')">
            {{ data.name }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('accountlink.msgamesLocalName')">
            {{ data.local_name }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('accountlink.msgamesJoined')">
            {{ data.joined }}
        </el-descriptions-item>
    </el-descriptions>
</template>

<script setup lang="ts">
import { utc_to_local_format } from '@/utils/system/tools';
import { PropType } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElDescriptions, ElDescriptionsItem} from 'element-plus';
const { t } = useI18n();

defineProps({
    data: {
        type: Object as PropType<any>,
        default() { return {}; },
    },
})

</script>