<template>
    <el-table-column v-slot="scope" :label="t('common.prop.realName')" width="auto">
        <span class="nobr">
            <PlayerName class="name" :user-id="scope.row.player__id" :user-name="scope.row.player__realname" />
        </span>
    </el-table-column>
</template>

<script setup lang="ts">
import { ElTableColumn } from 'element-plus';
import { useI18n } from 'vue-i18n';

import PlayerName from '../PlayerName.vue';

const { t } = useI18n();

</script>

<style lang="less">

.nobr {
    white-space: nowrap;
    hyphens: none;
}

</style>
