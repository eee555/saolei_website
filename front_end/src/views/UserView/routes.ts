import { RouteRecordRaw } from 'vue-router';

export const userRoutes: RouteRecordRaw[] = [
    {
        path: 'accountlink',
        name: 'user-accountlink',
        component: () => import('./UserAccountLinkView.vue'),
    },
    {
        path: 'record',
        name: 'user-record',
        component: () => import('./UserRecordView.vue'),
    },
    {
        path: 'summary',
        name: 'user-summary',
        component: () => import('./UserSummaryView.vue'),
    },
    {
        path: 'videos',
        name: 'user-videos',
        component: () => import('./UserVideoView.vue'),
    },
    {
        path: 'upload',
        name: 'user-upload',
        component: () => import('./UserUploadView.vue'),
    },
];
