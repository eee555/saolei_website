<template>
    <el-table-column
        prop="level"
        :filters="[{ text: t('common.level.b'), value: 'b' }, { text: t('common.level.i'), value: 'i' }, { text: t('common.level.e'), value: 'e' }]"
        :filter-method="defaultFilterMethod" :filter-multiple="false"
    >
        <template #default="scope">
            <GameLevelIcon :level="scope.row.level" />
        </template>
    </el-table-column>
</template>

<script setup lang="ts">

import { ElTableColumn } from 'element-plus';
import GameLevelIcon from '@/components/widgets/GameLevelIcon.vue';
import { defaultFilterMethod } from '@/utils';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

</script>
