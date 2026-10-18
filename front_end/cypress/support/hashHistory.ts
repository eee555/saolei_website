import { h } from 'vue';
import type { Router, RouteRecordRaw } from 'vue-router';
import { createRouter, createWebHashHistory } from 'vue-router';

import { unmountMountedComponent } from './mountedComponent';

const trackedRouters: Router[] = [];
let snapshot: { url: string; state: unknown } | null = null;

function captureHistoryState(state: unknown): unknown {
    if (state === null) return null;
    try {
        return structuredClone(state);
    } catch {
        return state;
    }
}

export function trackHashRouter<T extends Router>(router: T): T {
    trackedRouters.push(router);
    return router;
}

export function hashRouter(options: { routes?: RouteRecordRaw[]; initialPath?: string } = {}): Router {
    const router = createRouter({
        history: createWebHashHistory(),
        routes: options.routes ?? [{ path: '/:pathMatch(.*)*', component: { render: () => h('div') } }],
    });
    if (options.initialPath !== undefined) void router.push(options.initialPath);
    return trackHashRouter(router);
}

export function installHashHistoryCleanup(): void {
    beforeEach(() => {
        snapshot = null;
        cy.window().then((window) => {
            snapshot = { url: window.location.href, state: captureHistoryState(window.history.state) };
        });
    });

    afterEach(() => {
        cy.then(() => {
            unmountMountedComponent();
        });
        cy.then(() => {
            for (const router of trackedRouters.splice(0)) {
                router.options.history.destroy();
            }
        });
        cy.window().then((window) => {
            if (!snapshot) return;
            const { url, state } = snapshot;
            snapshot = null;
            window.history.replaceState(state, '', url);
        });
    });
}
