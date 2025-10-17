<template>
    第
    <el-input-number v-model="gscID" size="small" :min="0" />
    届
    <br>
    <el-tabs v-model="currentTab">
        <el-tab-pane label="基本信息" name="general" lazy>
            <GSCGeneralInfo :id="gscID" />
        </el-tab-pane>
        <el-tab-pane label="参赛选手" lazy>
            <GSCParticipants :id="gscID" />
        </el-tab-pane>
    </el-tabs>
</template>

<script setup lang="ts">

import { ElInputNumber, ElTabs, ElTabPane } from 'element-plus';
import { ref } from 'vue';
import GSCGeneralInfo from '@/components/GSCAdmin/GeneralInfo.vue';
import GSCParticipants from '@/components/GSCAdmin/Participants.vue';

const currentTab = ref('general');
const gscID = ref(0);

</script>
