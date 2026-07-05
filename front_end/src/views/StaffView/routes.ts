import type { RouteRecordRaw } from 'vue-router';

export const staffRoutes: RouteRecordRaw[] = [
    {
        path: 'userprofile',
        name: 'staff-userprofile',
        component: () => import('./UserProfile.vue'),
    },
    {
        path: 'videomodel',
        name: 'staff-videomodel',
        component: () => import('./VideoModel.vue'),
    },
    {
        path: 'accountlink',
        name: 'staff-accountlink',
        component: () => import('./AccountLink.vue'),
    },
    {
        path: 'identifier',
        name: 'staff-identifier',
        component: () => import('./Identifier.vue'),
    },
    {
        path: 'logs',
        name: 'staff-logs',
        component: () => import('./Logs.vue'),
    },
    {
        path: 'tournament',
        name: 'staff-tournament',
        component: () => import('./Tournament.vue'),
    },
    {
        path: 'task',
        name: 'staff-task',
        component: () => import('./Task.vue'),
    },
    {
        path: 'batchvideo',
        name: 'staff-batchvideo',
        component: () => import('./BatchUpdateVideo.vue'),
    },
    {
        path: 'batchpluck',
        name: 'staff-batchpluck',
        component: () => import('./BatchRefreshPLuck.vue'),
    },
];
