import type { RouteRecordRaw } from 'vue-router';

export const rankingRoutes: RouteRecordRaw[] = [
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
