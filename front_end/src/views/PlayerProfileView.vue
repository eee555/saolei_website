<template>
    <el-text tag="b" size="large">{{ $t('accountlink.title') }}</el-text>
    <AccountLinkManager />
</template>

<script setup lang="ts">
import AccountLinkManager from '@/components/AccountLinkManager.vue';
</script>