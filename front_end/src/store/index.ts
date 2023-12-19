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
