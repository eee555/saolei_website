<template>
    <el-descriptions border>
        <el-descriptions-item :label="t('common.prop.update_time')" :span="2">
            {{ utc_to_local_format(data.update_time) }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('accountlink.womTrophy')">
            {{ data.trophy }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('accountlink.womResource')" :span="3">
            <el-image src="https://minesweeper.online/img/other/hp.svg" class="icon" /><el-text style="vertical-align: middle;">
                {{ data.honour }}
            </el-text>&nbsp;
            <el-image src="https://minesweeper.online/img/other/coin.svg" class="icon" /><el-text style="vertical-align: middle;">
                {{ data.minecoin }}
            </el-text>&nbsp;
            <el-image src="https://minesweeper.online/img/gems/0.svg" class="icon" /><el-text style="vertical-align: middle;">
                {{ data.gem }}
            </el-text>&nbsp;
            <el-image src="https://minesweeper.online/img/arena-coins/0.svg" class="icon" /><el-text style="vertical-align: middle;">
                {{ data.coin }}
            </el-text>&nbsp;
            <Ticket class="icon" /><el-text style="vertical-align: middle;">
                {{ data.arena_ticket }}
            </el-text>&nbsp;
            <el-image src="https://minesweeper.online/img/eq.svg" class="icon" /><el-text style="vertical-align: middle;">
                {{ data.equipment }}
            </el-text>&nbsp;
            <el-image src="https://minesweeper.online/img/item/parts0.svg" class="icon" /><el-text style="vertical-align: middle;">
                {{ data.part }}
            </el-text>&nbsp;
        </el-descriptions-item>
        <el-descriptions-item :label="t('accountlink.womExperience')">
            {{ data.experience }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('accountlink.womArenaPoint')">
            {{ data.arena_point }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('accountlink.womMaxDifficulty')">
            {{ data.max_difficulty }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('accountlink.womWin')">
            {{ data.win }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('accountlink.womLastSeason')">
            {{ data.last_season }}
        </el-descriptions-item>
    </el-descriptions>
    <el-table :data="datatable">
        <el-table-column prop="category" />
        <el-table-column prop="b" :label="t('common.level.b')" />
        <el-table-column prop="i" :label="t('common.level.i')" />
        <el-table-column prop="e" :label="t('common.level.e')" />
    </el-table>
</template>

<script setup lang="ts">
import { ms_to_s } from '@/utils';
import { utc_to_local_format } from '@/utils/system/tools';
import { computed, PropType } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElDescriptions, ElDescriptionsItem, ElTable, ElTableColumn, ElText, ElImage } from 'element-plus';

const prop = defineProps({
    data: {
        type: Object as PropType<any>,
        default() { return {}; },
    },
});

const { t } = useI18n();

const datatable = computed(() => {
    return [
        { category: t('common.prop.time'), b: ms_to_s(prop.data.b_t_ms), i: ms_to_s(prop.data.i_t_ms), e: ms_to_s(prop.data.e_t_ms) },
        { category: t('common.prop.ioe'), b: prop.data.b_ioe, i: prop.data.i_ioe, e: prop.data.e_ioe },
        { category: t('common.prop.mastery'), b: prop.data.b_mastery, i: prop.data.i_mastery, e: prop.data.e_mastery },
        { category: t('common.prop.winstreak'), b: prop.data.b_winstreak, i: prop.data.i_winstreak, e: prop.data.e_winstreak },
    ];
});

</script>

<style lang="less" scoped>

.icon {
    height: 18px;
    vertical-align: middle;
}

</style>
