import { createStore } from 'vuex'

export default createStore({
  state: {
    user: [],   // 真正的用户
    player: [], // 访问我的地盘
  },
  getters: {

  },
  mutations: {
    updateUser(state, data) {
      state.user = data;
      // 样例：{id: 1, username: '1', realname: '22输电分22', is_banned: false}
    },
    updatePlayer(state, data) {
      state.player = data;
    }
  },
  actions: {
  },
  modules: {
  }
})
