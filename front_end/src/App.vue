<template>
  <div class="common-layout">
    <el-container>
      <el-header class="header_all" style="margin-bottom: 0px">
        <Login @login="user_login" @logout="user_logout"></Login>
        <nav>
          <router-link to="/" class="header">首页</router-link>
          <router-link to="/ranking" class="header">排行榜</router-link>
          <router-link to="/video" class="header">录像</router-link>
          <router-link to="/world" class="header">统计</router-link>
          <router-link to="/guide" class="header">教程</router-link>
          <router-link to="/player" class="header2" v-show="player_visibile">我的地盘</router-link>
          <router-link to="/upload" class="header2">上传录像</router-link>
          
        </nav>
      </el-header>


      <el-main>
        <div class="content">
          <router-view />
        </div>
      </el-main>


      <el-footer style="margin: auto;">
        Copyright @ 2008　扫雷网 Saolei.wang　版权所有　陕ICP备19026089号-1
      </el-footer>
    </el-container>
  </div>
</template>

<script setup lang='ts'>
import { ref, reactive, onMounted } from 'vue'
import Login from "./components/Login.vue";
import { LoginStatus } from "@/utils/common/structInterface"
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();

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




</script>

<style scope lang='less'>
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
  margin-left: 6%;
  margin-right: 6%;
  // background-color: #ddd;
}
</style>