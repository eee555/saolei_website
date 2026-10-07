import type { RouteRecordRaw } from 'vue-router';

export const rankingRoutes: RouteRecordRaw[] = [
    {
        path: 'speed',
        name: 'ranking_speed',
        component: () => import('./SpeedRanking.vue'),
        redirect: { name: 'ranking_speed_saolei' },
        children: [
            { path: 'saolei', name: 'ranking_speed_saolei', component: () => import('./SaoleiRanking.vue') },
            { path: 'pb', name: 'ranking_speed_pb', component: () => import('./PBRanking.vue') },
        ],
    },
    {
        path: 'density',
        name: 'ranking_density',
        component: () => import('./DensityRanking.vue'),
    },
    {
        path: 'tournament',
        name: 'ranking_tournament',
        component: () => import('./TournamentRanking.vue'),
    },
];
