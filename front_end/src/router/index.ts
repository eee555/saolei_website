import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router'


const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/ranking',
    name: 'ranking',
    component: () => import('../views/RankingView.vue')
  },
  {
    path: '/video',
    name: 'video',
    component: () => import('../views/VideoView.vue')
  },
  {
    path: '/world',
    name: 'world',
    component: () => import('../views/WorldView.vue')
  },
  {
    path: '/guide',
    name: 'guide',
    component: () => import('../views/GuideView.vue')
  },
  {
    path: '/guide/:name/:paragraph',
    name: 'guide',
    component: () => import('../views/GuideView.vue')
  },
  {
    path: '/score',
    name: 'score',
    component: () => import('../views/ScoreRankView.vue')
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../views/SettingView.vue')
  },
  {
    path: '/player/:id',
    name: 'player_id',
    component: () => import('../views/PlayerView.vue')
  },
  {
    path: '/player',
    name: 'player',
    component: () => import('../views/PlayerView.vue')
  },
  {
    path: '/upload',
    name: 'upload',
    component: () => import('../views/UploadView.vue')
  },
  {
    path: '/staff',
    name: 'staff',
    component: () => import('../views/StaffView.vue')
  },
]

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes
})

export default router
