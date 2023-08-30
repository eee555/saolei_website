import { createStore } from 'vuex'

export default createStore({
  state: {
    user: [],
    player: [],
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
