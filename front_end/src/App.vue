<template>
    <el-container style="height: 100%">
        <el-header height="fit-content">
            <Menu />
        </el-header>

        <el-container class="mainheight">
            <el-main class="common-layout">
                <VideoPlayer />
                <VideoListDialog />
                <router-view />
                <Footer />
            </el-main>
        </el-container>
    </el-container>

    <el-dialog
        v-if="false" v-model="notice_visible" draggable :lock-scroll="false" title="站长通知"
        :before-close="handle_notice_close" style="white-space: pre-wrap;" width="min(max(50%, 400px), 90vw)"
    >
        <span>{{ notice }}</span>
        <template #footer>
            <span class="dialog-footer">
                <el-checkbox v-model="never_show_notice">不再显示此对话框&nbsp;&nbsp;&nbsp;</el-checkbox>
                <base-button-confirm @click="handle_notice_close()" />
            </span>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
import { useDark, useToggle } from '@vueuse/core';
import { ElCheckbox, ElContainer, ElDialog, ElHeader, ElMain } from 'element-plus';
import { onMounted, ref, watch } from 'vue';

import BaseButtonConfirm from './components/common/BaseButtonConfirm.vue';
import VideoListDialog from './components/dialogs/VideoListDialog.vue';
import Footer from './components/Footer.vue';
import VideoPlayer from './components/VideoPlayer/App.vue';
import { local } from './store';
import Menu from './views/Menu.vue';

const isDark = useDark();
useToggle(isDark);
watch(isDark, (v) => {
    local.value.darkmode = v;
});

// const player_visible = ref(false)
const notice_visible = ref(false);
const never_show_notice = ref(false);

const notice = ref(`
0、即日起，网站正式上线！！！
1、开源扫雷网是社区共建的扫雷排名网站。在这里，你可以上传扫雷录像参与全球排名；也希望有开发能力的雷友可以发挥专业能力，为网站贡献代码、增加功能。
2、软件下载链接在页面最下方。
3、网站运营完全依赖赞助，希望有能力的雷友给与力所能及的帮助和支持，我们不胜感激。
4、相关意见、问题和建议请移步至此处https://gitee.com/ee55/saolei_website/issues发表。
`);

onMounted(() => {
    const notice_hash = localStorage.getItem('notice') as string;
    if (hash_code(notice.value) + '' != notice_hash) {
        notice_visible.value = true;
    }

    console.log(`
  开源扫雷网(openms.top)开发团队，期待您的加入: 2234208506@qq.com
  `);
    local.value.darkmode = isDark.value;
});

// const goback_home = () => {
//     router.push("/")
// }

// 站长通知关闭的回调
const handle_notice_close = () => {
    if (never_show_notice.value) {
        localStorage.setItem('notice', hash_code(notice.value) + '');
    }
    notice_visible.value = false;
};

function hash_code(t: string) {
    let hash = 0,
        i,
        chr;
    if (t.length === 0) return hash;
    for (i = 0; i < t.length; i++) {
        chr = t.charCodeAt(i);
        hash = (hash << 5) - hash + chr;
        hash |= 0; // 32bit integer
    }
    return hash;
}
</script>

<style lang="less">
body {
    margin: 0;
}
</style>

<style lang="less" scoped>
.el-header {
    --el-header-height: v-bind("`${local.menu_height}px`");
    padding: 0px;
}

.mainheight {
    height: calc(100svh - v-bind("`${local.menu_height}px`"))
}

@media (min-width: 1024px) {
  .common-layout {
    padding: 1.5em min(15vw, 150px);
    /* 这里设置只在大屏幕（电脑端）上生效的样式 */
  }
}

</style>

<style lang="less">
// 傻逼PrimeVue的bug，开发者还不当回事
// https://github.com/primefaces/primevue/issues/4093
// ElementPlus也不支持表格分页，只能先吃着PrimeVue这坨屎
.p-datatable-filter-overlay-popover {
    z-index: 3000 !important;
}

.p-select-overlay {
    z-index: 3000 !important;
}
</style>
