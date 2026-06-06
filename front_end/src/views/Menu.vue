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
            <IconMenuItem :text="t(`local.${item.index}`)" :icon="item.icon" />
        </el-menu-item>
        <div class="menu-spacer" />
        <el-menu-item v-if="store.user.id != 0" :index="player_url">
            <IconMenuItem :text="store.user.username" icon="User" />
        </el-menu-item>
        <el-menu-item v-if="store.user.is_staff" key="staff" index="/staff">
            <IconMenuItem :text="t('local.staff')" icon="Key" />
        </el-menu-item>
        <el-menu-item index="/settings" style="padding-left: 8px; padding-right: 5px">
            <IconMenuItem :text="t('local.setting')" icon="Setting" />
        </el-menu-item>
        <LanguagePicker v-show="local.language_show" style="padding-left: 8px; padding-right: 8px;" />
        <Login @keydown.stop />
    </el-menu>
</template>

<script setup lang="ts">
import { ElImage, ElMenu, ElMenuItem } from 'element-plus';
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
    { index: 'ranking', icon: 'Trophy' },
    { index: 'video', icon: 'VideoCameraFilled' },
    // { index: "world", icon: "Odometer" },
    { index: 'guide', icon: 'Document' },
    // { index: "score", icon: "Histogram" },
    { index: 'tournament', icon: 'Medal' },
    { index: 'server', icon: 'Cpu' },
] as const;

const player_url = computed(() => `/player/${store.user.id}`);

onMounted(() => {
    router.isReady().then(() => {
        menu_index.value = router.currentRoute.value.fullPath;
    });
});

const menuHeight = computed(() => `${local.value.menu_height}px`);

const i18nMessages = {
    'zh-cn': { local: {
        ranking: '排行榜',
        video: '录像',
        world: '统计',
        guide: '教程',
        score: '积分',
        staff: '管理',
        profile: '我的地盘',
        server: '服务器',
        setting: '设置',
        tournament: '比赛',
    } },
    'en': { local: {
        ranking: 'Ranking',
        video: 'Videos',
        world: 'Statistics',
        guide: 'Guides',
        score: 'Scores',
        profile: 'Profile',
        server: 'Server',
        setting: 'Settings',
        staff: 'Moderate',
        tournament: 'Tournament',
    } },
    'de': { local: {
        ranking: 'Ranking',
        video: 'Video',
        world: 'Welt',
        guide: 'Hilfe',
        score: 'Ergebnisse',
        profile: 'Profil',
    } },
    'pl': { local: {
        ranking: 'ranking',
        video: 'filmy',
        world: 'statystyki',
        guide: 'poradniki',
        score: 'wyniki',
        profile: 'profil',
    } },
};

const { t } = useI18n({ messages: i18nMessages });

</script>

<style lang="less" scoped>

.el-menu {
    line-height: v-bind("menuHeight");
    flex-wrap: wrap;
    justify-content: flex-end;
    height: fit-content;
}

.logo {
    cursor: pointer;
    justify-content: center;
    align-items: center;
    padding: v-bind("`${local.menu_height / 8}px`");
}

.logo1 {
    width: v-bind("menuHeight");
    height: v-bind("menuHeight");
    margin-top: 4px;
    margin-bottom: 4px;
    display: inline-flex;
}

.logo2 {
    height: v-bind("menuHeight");
    display: inline-flex;
}

.menu-spacer {
    flex-grow: 1;
}

.el-menu-item {
    font-size: v-bind("`${local.menu_font_size}px`");
    padding-left: 8px;
    padding-right: 5px;
    height: v-bind("menuHeight");
}

</style>
