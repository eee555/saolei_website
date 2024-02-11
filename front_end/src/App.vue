<template>
  <div class="common-layout">
    <el-container>
      <el-main class="header_all" style="padding-top: 0;overflow: hidden;">
        <div class="logo-container">
          <div @click="goback_home()" class="logo" style="float:inline-start;">
            <el-image style="width: 72px; height: 72px;" :src="logo_1" :fit="'cover'" />
            <el-image style="width: 162px; height: 74px;" :src="logo_2" :fit="'cover'" />
          </div>
          <div style="float: inline-end; ">
            <Menu @login="user_login" @logout="user_logout" style="margin-bottom: 10px;"></Menu>
          </div>

        </div>
        <div style="clear:both;"></div>
        <nav>
          <router-link to="/" class="header">首页</router-link>
          <router-link to="/ranking" class="header">排行榜</router-link>
          <router-link to="/video" class="header">录像</router-link>
          <router-link to="/world" class="header">统计</router-link>
          <router-link to="/guide" class="header">教程</router-link>
          <router-link to="/player" class="header2" v-show="player_visibile">我的地盘</router-link>
          <router-link to="/upload" class="header2">上传录像</router-link>

        </nav>
        <!-- </el-header> -->


        <!-- <el-main> -->
        <div class="content" style="padding-top: 16px;">
          <router-view />
        </div>
      </el-main>


      <el-footer style="margin: auto;">
        Copyright @ 2023　<a href="http://fff666.top">扫雷网 fff666.top</a>　版权所有　<a
          href="https://beian.miit.gov.cn/">苏ICP备2023056839号-1</a>
        <span style="width:12px; display:inline-block"></span>
        <a href="https://beian.mps.gov.cn/#/query/webSearch?code=32020602001691" rel="noreferrer"
          target="_blank">苏公网安备32020602001691</a>
      </el-footer>
    </el-container>
  </div>

  <el-dialog draggable :lock-scroll="false" v-model="notice_visible" title="站长通知" width="30%" :before-close="handle_notice_close">
    <span>{{ notice }}</span>
    <template #footer>
      <span class="dialog-footer">
        <el-checkbox v-model="never_show_notice">不再显示此对话框</el-checkbox>
        <el-button type="primary" @click="handle_notice_close();">
          确认
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang='ts'>
import { ref, reactive, onMounted } from 'vue'
import Menu from "./components/Menu.vue";
import { LoginStatus } from "@/utils/common/structInterface"
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
const logo_1 = ref(require('@/assets/logo.png'))
const logo_2 = ref(require('@/assets/logo2.png'))

import { useRouter } from 'vue-router'
const router = useRouter()

const player_visibile = ref(false)
const notice_visible = ref(false)
const never_show_notice = ref(false)
const tab_width = ref("16%")

// let refLogin = ref<any>(null)

const notice = ref(`
1、本站正在进行的是第二轮删档内测，但是链接请勿传到群外（出于网络安全、网站安全方面考虑）。
2、相关意见和建议请先检查群内公告文档里的待办、已有issue，若没有同类问题，再在此处[https://gitee.com/ee55/saolei_website/issues]发表。
3、招募管理员，负责少量审核、解冻录像、封禁违规用户、为填错名字的用户增加修改名字的次数。
`)

onMounted(() => {
  const notice_hash = localStorage.getItem("notice") as String;
  if (hash_code(notice.value) + "" != notice_hash) {
    notice_visible.value = true;
  }

  console.log(`
  元扫雷网(fff666.top)开发团队，期待您的加入: 2234208506@qq.com
  `);


})


const user_login = () => {
  player_visibile.value = true;
  tab_width.value = "14%";
}

const user_logout = () => {
  player_visibile.value = false;
  tab_width.value = "16%";
  proxy.$router.push("/");
}

const goback_home = () => {
  router.push("/")
}

// 站长通知关闭的回调
const handle_notice_close = () => {
  if (never_show_notice.value) {
    localStorage.setItem("notice", hash_code(notice.value) + "");
  }
  notice_visible.value = false;
}

const hash_code = function (t: string) {
  var hash = 0, i, chr;
  if (t.length === 0) return hash;
  for (i = 0; i < t.length; i++) {
    chr = t.charCodeAt(i);
    hash = ((hash << 5) - hash) + chr;
    hash |= 0; // 32bit integer
  }
  return hash;
};




</script>

<style scope lang='less'>
.logo-container {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: flex-end;
}

.logo:hover {
  cursor: pointer;
}

.header {
  background-color: #ececec;
  float: left;
  width: v-bind("tab_width");
  height: 36px;
  display: block;
  text-align: center;
  padding-top: 8px;
  font-size: 20px;
  border-left: 1px #fff solid;
  border-right: 1px #fff solid;

}

.header2 {
  background-color: #ececec;
  float: left;
  width: v-bind("tab_width");
  height: 36px;
  display: block;
  text-align: center;
  padding-top: 8px;
  font-size: 20px;
  border-left: 1px #fff solid;
  border-right: 1px #fff solid;

}

/*设置点击前的样式 */
a {
  text-decoration: none;
  color: #000;
}

/*设置点击后的样式 */
.router-link-active {
  text-decoration: none;
  color: #000;
}

.header_all {
  margin-left: 5%;
  margin-right: 5%;
}

.content {
  clear: both;
  margin-left: 3%;
  margin-right: 3%;
}
</style>
