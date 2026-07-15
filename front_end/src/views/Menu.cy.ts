import * as ELIcons from '@element-plus/icons-vue';
import { createMemoryHistory, createRouter } from 'vue-router';

import Menu from './Menu.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { local, store } from '@/store';
import { pinia } from '@/store/create';

const user = {
    id: 42,
    username: 'tester',
    realname: 'Tester',
    is_staff: true,
};

const routes = [
    { path: '/', component: { template: '<div />' } },
    { path: '/ranking', component: { template: '<div />' } },
    { path: '/video', component: { template: '<div />' } },
    { path: '/guide', component: { template: '<div />' } },
    { path: '/tournament', component: { template: '<div />' } },
    { path: '/server', component: { template: '<div />' } },
    { path: '/player/:id', component: { template: '<div />' } },
    { path: '/staff', component: { template: '<div />' } },
    { path: '/settings', component: { template: '<div />' } },
];

type MenuRects = Record<string, DOMRect>;

function mountMenu(width: number) {
    cy.viewport(width, 300);
    cy.intercept('GET', '**/api/userprofile/info/0', user).as('fetchUser');

    local.value.language = 'en';
    local.value.language_show = true;
    local.value.menu_font_size = 18;
    local.value.menu_height = 60;
    local.value.menu_icon = false;
    store.login(user);

    const router = createRouter({
        history: createMemoryHistory(),
        routes,
    });

    void router.push('/');
    cy.wrap(router.isReady()).then(() => {
        cy.mount(Menu, {
            global: {
                plugins: [pinia, router, i18n],
                components: ELIcons,
                config: {
                    globalProperties: {
                        $axios,
                    },
                },
            },
        });
    });
    cy.wait('@fetchUser');
}

function getMenuRects() {
    return cy.get('.el-menu').then((menu) => {
        const getRect = (selector: string) => menu.find(selector)[0].getBoundingClientRect();

        return {
            menu: menu[0].getBoundingClientRect(),
            ranking: getRect('.el-menu-item:contains("Ranking")'),
            server: getRect('.el-menu-item:contains("Server")'),
            profile: getRect(`.el-menu-item:contains("${user.username}")`),
            staff: getRect('.el-menu-item:contains("Moderate")'),
            docs: getRect('.el-menu-item:contains("Docs")'),
            settings: getRect('.el-menu-item:contains("Settings")'),
            language: getRect('.el-dropdown'),
            logout: getRect('.fakemenuitem:contains("Logout")'),
        } satisfies MenuRects;
    });
}

describe('<Menu /> layout', () => {
    it('keeps the menu on one row when there is enough width', () => {
        mountMenu(1280);

        getMenuRects().then((rects) => {
            const itemTops = [
                rects.ranking.top,
                rects.server.top,
                rects.profile.top,
                rects.staff.top,
                rects.docs.top,
                rects.settings.top,
                rects.language.top,
                rects.logout.top,
            ];

            expect(Math.max(...itemTops) - Math.min(...itemTops)).to.be.lessThan(3);
        });
    });

    it('lets right-side items wrap individually and keeps wrapped items right aligned', () => {
        mountMenu(920);

        getMenuRects().then((rects) => {
            const firstRowTop = rects.server.top;
            const rightItems = [
                rects.profile,
                rects.staff,
                rects.docs,
                rects.settings,
                rects.language,
                rects.logout,
            ];
            const firstRowRightItems = rightItems.filter((rect) => Math.abs(rect.top - firstRowTop) < 3);
            const wrappedRightItems = rightItems.filter((rect) => rect.top - firstRowTop > 10);

            expect(firstRowRightItems.length, 'right-side items still fitting on the first row').to.be.greaterThan(0);
            expect(wrappedRightItems.length, 'right-side items wrapped to the second row').to.be.greaterThan(0);
            expect(rects.logout.right, 'last wrapped item is aligned to menu right edge').
                to.be.closeTo(rects.menu.right, 3);
        });
    });
});
