<template>
    <span class="text">第</span>
    <ElInputNumber v-model="gscID" size="small" :min="0" />
    <span class="text">届</span>
    <br>
    <GSCGeneralInfo :id="gscID" />
</template>

<script setup lang="ts">
import { ElInputNumber } from 'element-plus';
import { ref } from 'vue';

import '@/styles/text.css';
import GSCGeneralInfo from '@/components/GSCAdmin/GeneralInfo.vue';

const gscID = ref(0);
</script>
