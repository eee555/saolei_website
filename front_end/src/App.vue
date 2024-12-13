<template>
    <el-container style="height: 100%">
        <el-header>
            <el-scrollbar :height="100"> <!-- 给一个足够的高度就可以不显示纵向滚动条 -->
                <el-menu mode="horizontal" :router="true" :default-active="menu_index" :ellipsis="false"
                    menu-trigger="click">
                    <el-menu-item index="/" class="logo">
                        <el-image class="logo1" :src="logo_1" :fit="'cover'" />
                        <el-image v-if="!local.menu_icon" class="logo2" :src="logo_2" :fit="'cover'" />
                    </el-menu-item>
                    <el-menu-item v-for="item in menu_items" :index="'/' + item.index">
                        <IconMenuItem :text="$t(item.content)" :icon="item.icon" />
                    </el-menu-item>
                    <div style="flex-grow: 1" />
                    <el-menu-item :index="player_url" v-if="store.user.id != 0">
                        <IconMenuItem :text="store.user.username" icon="User" />
                    </el-menu-item>
                    <el-menu-item index="/settings" style="padding-left: 8px; padding-right: 5px">
                        <el-badge is-dot :hidden="true" :offset="[0,15]">
                            <IconMenuItem :text="$t('menu.setting')" icon="Setting" />
                        </el-badge>
                    </el-menu-item>
                    <LanguagePicker v-show="local.language_show" style="padding-left: 8px; padding-right: 8px;" />
                    <Login @login="user_login" @logout="user_logout"></Login>
                </el-menu>
            </el-scrollbar>
        </el-header>

        <el-container class="mainheight">
            <el-main class="common-layout">
                <PlayerDialog />
                <router-view />
                <Footer />
            </el-main>
        </el-container>
    </el-container>

    <el-dialog draggable :lock-scroll="false" v-model="notice_visible" title="站长通知"
        :before-close="handle_notice_close" style="white-space: pre-wrap;" width="min(max(50%, 400px), 90vw)">
        <span>{{ notice }}</span>
        <template #footer>
            <span class="dialog-footer">
                <el-checkbox v-model="never_show_notice">不再显示此对话框&nbsp;&nbsp;&nbsp;</el-checkbox>
                <el-button type="primary" @click="handle_notice_close()">
                    确认
                </el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import LanguagePicker from "./components/widgets/LanguagePicker.vue";
import IconMenuItem from "./components/widgets/IconMenuItem.vue";
import Login from "./components/Login.vue";
import Footer from "./components/Footer.vue";
import PlayerDialog from "./components/PlayerDialog.vue";
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import { store, local } from "./store";

import { useI18n } from "vue-i18n";
const t = useI18n();

const { proxy } = useCurrentInstance();
import logo_1 from "@/assets/logo.png";
import logo_2 from "@/assets/logo2.png";

import { useRouter } from "vue-router";
const router = useRouter();

import { useDark, useToggle } from '@vueuse/core';
const isDark = useDark()
useToggle(isDark)

// const player_visible = ref(false)
const notice_visible = ref(false);
const never_show_notice = ref(false);

// 主要是切换后的高亮
const menu_index = ref();

const menu_items = [
    { index: "ranking", icon: "Trophy", content: "menu.ranking" },
    { index: "video", icon: "VideoCameraFilled", content: "menu.video" },
    //{ index: "world", icon: "Odometer", content: "menu.world" },
    { index: "guide", icon: "Document", content: "menu.guide" },
    //{ index: "score", icon: "Histogram", content: "menu.score" },
];

const notice = ref(`
0、即日起，网站正式上线！！！
1、开源扫雷网是社区共建的扫雷排名网站。在这里，你可以上传扫雷录像参与全球排名；也希望有开发能力的雷友可以发挥专业能力，为网站贡献代码、增加功能。
2、软件下载链接在页面最下方。
3、网站运营完全依赖赞助，希望有能力的雷友给与力所能及的帮助和支持，我们不胜感激。
4、相关意见、问题和建议请移步至此处https://gitee.com/ee55/saolei_website/issues发表。
`);

onMounted(() => {
    const notice_hash = localStorage.getItem("notice") as String;
    if (hash_code(notice.value) + "" != notice_hash) {
        notice_visible.value = true;
    }

    console.log(`
  开源扫雷网(openms.top)开发团队，期待您的加入: 2234208506@qq.com
  `);
    router.isReady().then(() => {
        menu_index.value = router.currentRoute.value.fullPath;
    });
});

const player_url = computed(() => {
    return "/player/" + store.user.id;
});

const user_login = () => {
    // player_visible.value = true;
    // tab_width.value = "14vw";
};

const user_logout = () => {
    // console.log(router.currentRoute.value.fullPath);
    // 如果切在我的地盘，就切到主页
    if (router.currentRoute.value.fullPath.slice(0, 7) == "/player") {
        menu_index.value = "/";
        proxy.$router.push("/");
    }
};

// const goback_home = () => {
//     router.push("/")
// }

// 站长通知关闭的回调
const handle_notice_close = () => {
    if (never_show_notice.value) {
        localStorage.setItem("notice", hash_code(notice.value) + "");
    }
    notice_visible.value = false;
};

const hash_code = function (t: string) {
    var hash = 0,
        i,
        chr;
    if (t.length === 0) return hash;
    for (i = 0; i < t.length; i++) {
        chr = t.charCodeAt(i);
        hash = (hash << 5) - hash + chr;
        hash |= 0; // 32bit integer
    }
    return hash;
};
</script>

<style lang="less">
body {
    margin: 0;
}
</style>

<style lang="less" scoped>
.el-header {
    --el-header-height: v-bind("local.menu_height + 'px'");
    padding: 0px;
}

.el-menu {
    height: v-bind("local.menu_height + 'px'");
}

.logo {
    cursor: pointer;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    padding: 0px;
    padding-left: v-bind("local.menu_height / 8 + 'px'");
    padding-right: v-bind("local.menu_height / 8 + 'px'");
}

.logo1 {
    width: v-bind("local.menu_height - 8 + 'px'");
    height: v-bind("local.menu_height - 8 + 'px'");
    padding-top: 4px;
    padding-bottom: 4px;
    display: inline-flex;
}

.logo2 {
    width: v-bind("local.menu_height * 2.5 + 'px'");
    height: v-bind("local.menu_height + 'px'");
    display: inline-flex;
}

.el-menu-item {
    font-size: v-bind("local.menu_font_size + 'px'");
    padding-left: 8px;
    padding-right: 5px;
}

.mainheight {
    height: calc(100svh - v-bind("local.menu_height + 'px'"))
}

@media (min-width: 1024px) {  
  .common-layout {  
    padding: 1.5em max(20vw, 200px);
    /* 这里设置只在大屏幕（电脑端）上生效的样式 */  
  }  
}

</style>
