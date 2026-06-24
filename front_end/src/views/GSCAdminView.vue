<template>
    <span class="text">第</span>
    <ElInputNumber v-model="gscID" size="small" :min="0" />
    <span class="text">届</span>
    <br>
    <ElTabs v-model="currentTab">
        <ElTabPane label="基本信息" name="general" lazy>
            <GSCGeneralInfo :id="gscID" />
        </ElTabPane>
        <ElTabPane label="参赛选手" lazy>
            <GSCParticipants :id="gscID" />
        </ElTabPane>
    </ElTabs>
</template>

<script setup lang="ts">
import { ElInputNumber, ElTabPane, ElTabs } from 'element-plus';
import { ref } from 'vue';

import '@/styles/text.css';
import GSCGeneralInfo from '@/components/GSCAdmin/GeneralInfo.vue';
import GSCParticipants from '@/components/GSCAdmin/Participants.vue';

const currentTab = ref('general');
const gscID = ref(0);
</script>
