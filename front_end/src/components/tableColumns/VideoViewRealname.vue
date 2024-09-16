<template>
    <el-table-column :label="$t('common.prop.realName')" v-slot="scope" width="auto">
        <span class="nobr">
            <PlayerName class="name" :user_id="scope.row.player__id" :user_name="scope.row.player__realname" />
        </span>
    </el-table-column>
</template>

<script setup lang="ts">

import PlayerName from '../PlayerName.vue';

</script>

<style lang="less">

.nobr {
    white-space: nowrap;
    hyphens: none;
}

</style>