import type { RouteRecordRaw } from 'vue-router';

export const userRoutes: RouteRecordRaw[] = [
    {
        path: 'accountlink',
        name: 'guide-accountlink',
        component: () => import('./AccountLinks.vue'),
    },
];
