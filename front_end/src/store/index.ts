import { createStore } from 'vuex'

export default createStore({
  state: {
    user: {
      // 此id为用户的id从1开始，而不是数据库的自增id
      id: 0,
      username: "",
      realname: "",
      is_banned: false
    },   // 真正的用户
    // 访问谁的地盘不再具有记忆性。即点“我的地盘”，将永远是“我”的地盘
    // 想要访问特定用户，可以用url
  },
  getters: {

  },
  mutations: {
    updateUser(state, data) {
      state.user = data;
      // 样例：{id: 1, username: '1', realname: '22输电分22', is_banned: false}
    },
    updateUserRealname(state, data) {
      state.user.realname = data;
      // 样例：{id: 1, username: '1', realname: '22输电分22', is_banned: false}
    },
    // updatePlayer(state, data) {
    //   state.player = data;
    // }
  },
  actions: {
  },
  modules: {
  }
})
