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
                        <IconMenuItem :text="$t('menu.setting')" icon="Setting" />
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

    <el-dialog draggable :lock-scroll="false" v-model="notice_visible" title="站长通知" width="30%"
        :before-close="handle_notice_close">
        <span style="white-space: pre-wrap; ">{{ notice }}</span>
        <template #footer>
            <span class="dialog-footer">
                <el-checkbox v-model="never_show_notice">不再显示此对话框</el-checkbox>
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
import { useLocalStore, useUserStore } from "./store";
const store = useUserStore();
const local = useLocalStore();

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
0、公测已接近尾声。公测结束后，在正式上线之前会删除所有数据。
1、因为以下内容很重要，请在分享元扫雷网链接时务必分享本通知。
2、未来会实现从其他网站导入成绩的功能，所以无需重复上传在其他网站上已有的成绩。
3、一些个人信息功能（如姓名）还存在问题，所以个人信息暂时可以乱填，将来修复完毕后我们会给用户增加一次修改机会。
4、因为服务器配置是最丐的，日活增加后可能变卡。如果受不了的话请提供服务器/赞助加钱升级服务器。
5、标识审核暂时遵循严格匹配，产生不匹配警告后用户仍可点击黄色上传按钮使录像进入人工审核，通过后该标识就会进入用户的标识列表。出于审核效率考量，我们建议用户一次只上传一个标识不匹配录像，待标识通过之后再继续上传。
6、请忽略用户协议。
7、第一次加载时需要缓存资源，会很卡，尤其是教程页。第二次就快了。
8、相关意见、问题和建议请移步至此处[https://gitee.com/ee55/saolei_website/issues]发表。
`);

onMounted(() => {
    const notice_hash = localStorage.getItem("notice") as String;
    if (hash_code(notice.value) + "" != notice_hash) {
        notice_visible.value = true;
    }

    console.log(`
  元扫雷网(fff666.top)开发团队，期待您的加入: 2234208506@qq.com
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
    width: v-bind("local.menu_height * 2.17 + 'px'");
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
</style>
