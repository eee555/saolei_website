import { createStore } from 'vuex'

export default createStore({
  state: {
    user: {
      id: 0,
      username: "",
      realname: "",
      is_banned: false
    },   // 真正的用户
    // player: [], // 访问我的地盘（放弃。放到localstorage）
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
