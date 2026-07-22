<template>
    <div>
        <ElContainer>
            <ElMain style="padding: 1%;">
                <ElTabs type="border-card" style=" min-height: 300px;">
                    <NewsQueue />
                </ElTabs>
                <ElTabs v-model="active_tab" type="border-card" style="margin-top: 2%;">
                    <NewestQueue :is-active="active_tab === 'newest'" />
                    <ReviewQueue />
                </ElTabs>
            </ElMain>
        </ElContainer>
    </div>
</template>

<script setup lang='ts'>
import '@/styles/text.css';

import { ElContainer, ElMain, ElTabs } from 'element-plus';
import { ref } from 'vue';

import NewestQueue from './NewestQueue.vue';
import NewsQueue from './NewsQueue.vue';
import ReviewQueue from './ReviewQueue.vue';

const active_tab = ref('newest');
</script>

<style lang='less'>
.bottom_tabs {
    overflow: auto;
}

.aside-tip-title {
    font-size: 14px;
    display: flex;
    align-items: center;
    margin-top: 5%;
}

.text-button:hover {
    cursor: pointer;
}
</style>
