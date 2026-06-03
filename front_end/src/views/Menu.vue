<template>
    <el-menu
        mode="horizontal" :router="true" :default-active="menu_index" :ellipsis="false"
        menu-trigger="click"
    >
        <el-menu-item index="/" class="logo">
            <el-image class="logo1" :src="logo_1" :fit="'cover'" />
            <el-image v-if="!local.menu_icon" class="logo2" :src="logo_2" :fit="'cover'" />
        </el-menu-item>
        <el-menu-item v-for="item in menu_items" :key="item.index" :index="`/${ item.index}`">
            <IconMenuItem :text="t(item.content)" :icon="item.icon" />
        </el-menu-item>
        <div style="flex-grow: 1" />
        <el-menu-item v-if="store.user.id != 0" :index="player_url">
            <IconMenuItem :text="store.user.username" icon="User" />
        </el-menu-item>
        <el-menu-item v-if="store.user.is_staff" key="staff" index="/staff">
            <IconMenuItem :text="t('menu.staff')" icon="Key" />
        </el-menu-item>
        <el-menu-item index="/settings" style="padding-left: 8px; padding-right: 5px">
            <el-badge is-dot :hidden="true" :offset="[0,15]">
                <IconMenuItem :text="t('menu.setting')" icon="Setting" />
            </el-badge>
        </el-menu-item>
        <LanguagePicker v-show="local.language_show" style="padding-left: 8px; padding-right: 8px;" />
        <Login @keydown.stop />
    </el-menu>
</template>

<script setup lang="ts">
import { ElBadge, ElImage, ElMenu, ElMenuItem } from 'element-plus';
import { computed, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import logo_1 from '@/assets/logo.png';
import logo_2 from '@/assets/logo2.png';
import Login from '@/components/Login/App.vue';
import IconMenuItem from '@/components/widgets/IconMenuItem.vue';
import LanguagePicker from '@/components/widgets/LanguagePicker.vue';
import { local, store } from '@/store';

const menu_index = ref();
const router = useRouter();

const menu_items = [
    { index: 'ranking', icon: 'Trophy', content: 'menu.ranking' },
    { index: 'video', icon: 'VideoCameraFilled', content: 'menu.video' },
    // { index: "world", icon: "Odometer", content: "menu.world" },
    { index: 'guide', icon: 'Document', content: 'menu.guide' },
    // { index: "score", icon: "Histogram", content: "menu.score" },
    { index: 'tournament', icon: 'Medal', content: 'menu.tournament' },
    { index: 'server', icon: 'Cpu', content: 'menu.server' },
] as const;

const player_url = computed(() => `/player/${store.user.id}`);

onMounted(() => {
    router.isReady().then(() => {
        menu_index.value = router.currentRoute.value.fullPath;
    });
});

const { t } = useI18n();

</script>

<style lang="less" scoped>

.el-menu {
    height: v-bind("`${local.menu_height}px`");
}

.logo {
    cursor: pointer;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    padding: 0px;
    padding-left: v-bind("`${local.menu_height / 8}px`");
    padding-right: v-bind("`${local.menu_height / 8}px`");
}

.logo1 {
    width: v-bind("`${local.menu_height - 8}px`");
    height: v-bind("`${local.menu_height - 8}px`");
    padding-top: 4px;
    padding-bottom: 4px;
    display: inline-flex;
}

.logo2 {
    width: v-bind("`${local.menu_height * 2.5}px`");
    height: v-bind("`${local.menu_height}px`");
    display: inline-flex;
}

.el-menu-item {
    font-size: v-bind("`${local.menu_font_size}px`");
    padding-left: 8px;
    padding-right: 5px;
}

</style>
