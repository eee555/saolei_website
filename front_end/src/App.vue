<template>
  <div class="common-layout">
    <el-container>
      <el-main class="header_all" style="padding-top: 0;">
        <!-- <el-header class="header_all" style="margin-bottom: 0px"> -->
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
        Copyright @ 2023　<a href="fff666.top">扫雷网 fff666.top</a>　版权所有　<a
          href="https://beian.miit.gov.cn/">苏ICP备2023056839号-1</a>
        <span style="width:12px; display:inline-block"></span>
        <a href="https://beian.mps.gov.cn/#/query/webSearch?code=32020602001691" rel="noreferrer"
          target="_blank">苏公网安备32020602001691</a>
      </el-footer>
    </el-container>
  </div>
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
const tab_width = ref("16%")

// let refLogin = ref<any>(null)

// onMounted(() => {
//   console.log(666);
//   console.log(refLogin.value.login_status);
//   console.log(LoginStatus.IsLogin);
// })


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
  // background-color: #ddd;
}
</style>