import type { RouteRecordRaw } from 'vue-router';
import { createRouter, createWebHashHistory } from 'vue-router';

import { staffRoutes } from '@/views/StaffView/routes';
import { rankingRoutes } from '@/views/RankingView/routes';
import { userRoutes } from '@/views/UserView/routes';

const routes: RouteRecordRaw[] = [
    {
        path: '/',
        name: 'home',
        component: () => import('../views/HomeView.vue'),
    },
    {
        path: '/ranking',
        name: 'ranking',
        component: () => import('../views/RankingView/App.vue'),
        redirect: '/ranking/speed',
        children: rankingRoutes,
    },
    {
        path: '/video',
        name: 'video',
        component: () => import('../views/VideoView.vue'),
    },
    {
        path: '/world',
        name: 'world',
        component: () => import('../views/WorldView.vue'),
    },
    {
        path: '/guide',
        name: 'guide',
        component: () => import('../views/GuideView.vue'),
    },
    {
        path: '/guide/:name',
        name: 'guide_name',
        component: () => import('../views/GuideView.vue'),
    },
    {
        path: '/guide/:name/:paragraph',
        name: 'guide_name_paragraph',
        component: () => import('../views/GuideView.vue'),
    },
    {
        path: '/server',
        name: 'server',
        component: () => import('../views/ServerView/App.vue'),
    },
    {
        path: '/settings',
        name: 'settings',
        component: () => import('../views/SettingView/App.vue'),
    },
    {
        path: '/player/:id',
        name: 'player_id',
        component: () => import('../views/UserView/App.vue'),
        redirect: (to) => {
            const { id } = to.params;
            if (typeof id !== 'string') return '/player/0/summary';

            return `/player/${id}/summary`;
        },
        children: userRoutes,
    },
    {
        path: '/staff',
        name: 'staff',
        component: () => import('../views/StaffView/App.vue'),
        redirect: '/staff/userprofile',
        children: staffRoutes,
    },
    {
        path: '/tournament/:id',
        name: 'tournament_id',
        component: () => import('../views/TournamentView/TournamentView.vue'),
    },
    {
        path: '/tournament',
        name: 'tournament',
        component: () => import('../views/TournamentView/TournamentView.vue'),
    },
    {
        path: '/gsc/admin',
        name: 'gsc_admin',
        component: () => import('../views/GSCAdminView.vue'),
    },
];

const router = createRouter({
    history: createWebHashHistory(import.meta.env.BASE_URL),
    routes,
});

export default router;
