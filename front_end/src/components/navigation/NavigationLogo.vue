<template>
    <img class="site-brand__icon" :src="logo" alt="">
    <img class="site-brand__wordmark" :src="local.darkmode ? wordmarkDark : wordmark" alt="">
</template>

<script setup lang="ts">
import logo from '@/assets/logo.svg';
import wordmarkDark from '@/assets/logo2-dark.png';
import wordmark from '@/assets/logo2.png';
import { local } from '@/store';
</script>
