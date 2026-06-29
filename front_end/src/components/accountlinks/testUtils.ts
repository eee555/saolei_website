import type { Component } from 'vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { store } from '@/store';
import { pinia } from '@/store/create';
import type {
    AccountBilibiliResponse,
    AccountLinksResponse,
    AccountMSGamesResponse,
    AccountSaoleiResponse,
    AccountWoMResponse,
} from '@/utils/accountlinks';
import { AccountLinkPlatform } from '@/utils/accountlinks';
import { UserProfile } from '@/utils/userprofile';

function mountOptions(props: Record<string, unknown> = {}) {
    return {
        props,
        global: {
            plugins: [i18n, pinia],
            config: {
                globalProperties: {
                    $axios,
                },
            },
        },
    };
}

export function mountAccountLink(component: Component, props: Record<string, unknown> = {}): Cypress.Chainable<unknown> {
    return cy.mount(component as never, mountOptions(props) as never) as Cypress.Chainable<unknown>;
}

export function resetAccountLinkStore(userId = 1, playerId = 1): void {
    store.user = new UserProfile();
    store.player = new UserProfile();
    store.user.id = userId;
    store.player.id = playerId;
}

export function mockSaoleiResponse(overrides: Partial<AccountSaoleiResponse> = {}): AccountSaoleiResponse {
    return {
        id: 101,
        parent: 1,
        update_time: '2025-01-05T08:09:10Z',
        video_import_task: null,
        name: 'Saolei Player',
        total_views: 9876,
        beg_count: 12,
        int_count: 8,
        exp_count: 4,
        b_t_ms: 12340,
        i_t_ms: 45670,
        e_t_ms: 99990,
        s_t_ms: 158000,
        b_b_cent: 20,
        i_b_cent: 30,
        e_b_cent: 40,
        s_b_cent: 90,
        ...overrides,
    };
}

export function mockMSGamesResponse(overrides: Partial<AccountMSGamesResponse> = {}): AccountMSGamesResponse {
    return {
        id: 202,
        parent: 2,
        update_time: '2025-02-06T09:10:11Z',
        name: 'AM Player',
        local_name: 'Local AM',
        joined: '2024-01-01T00:00:00Z',
        ...overrides,
    };
}

export function mockWoMResponse(overrides: Partial<AccountWoMResponse> = {}): AccountWoMResponse {
    return {
        id: 303,
        parent: 3,
        update_time: '2025-03-07T10:11:12Z',
        trophy: 123,
        experience: 456,
        honour: 7,
        minecoin: 8,
        gem: 9,
        coin: 10,
        arena_ticket: 11,
        equipment: 12,
        part: 13,
        arena_point: 14,
        max_difficulty: 15,
        win: 16,
        last_season: 17,
        b_t_ms: 12000,
        i_t_ms: 45000,
        e_t_ms: 99000,
        b_ioe: 1.23,
        i_ioe: 2.34,
        e_ioe: 3.45,
        b_mastery: 88,
        i_mastery: 77,
        e_mastery: 66,
        b_winstreak: 5,
        i_winstreak: 6,
        e_winstreak: 7,
        ...overrides,
    };
}

export function mockBilibiliResponse(overrides: Partial<AccountBilibiliResponse> = {}): AccountBilibiliResponse {
    return {
        id: 404,
        parent: 4,
        update_time: '2025-04-08T11:12:13Z',
        name: 'Bili Player',
        face: 'http://i2.hdslb.com/bfs/app/avatar.png',
        sign: 'Keep mining',
        level: 6,
        following: 11,
        follower: 22,
        video_count: 33,
        article_count: 44,
        opus_count: 55,
        official_title: 'Official Miner',
        ...overrides,
    };
}

export function mockAccountLinksResponse(): AccountLinksResponse {
    return {
        summary: [
            { id: 1, platform: AccountLinkPlatform.Bilibili, identifier: '404', userprofile: 1, verified: true },
            { id: 2, platform: AccountLinkPlatform.WoM, identifier: '303', userprofile: 1, verified: true },
            { id: 3, platform: AccountLinkPlatform.MSGames, identifier: '202', userprofile: 1, verified: true },
            { id: 4, platform: AccountLinkPlatform.Saolei, identifier: '101', userprofile: 1, verified: true },
        ],
        B: mockBilibiliResponse(),
        c: mockSaoleiResponse(),
        a: mockMSGamesResponse(),
        w: mockWoMResponse(),
        q: null,
    };
}

export function mockSaoleiImportSummary(): void {
    cy.intercept('GET', '**/accountlink/saolei/videoimport/stat/**', {
        statusCode: 200,
        body: {
            bulk_task_status: 'NULL',
            total: 3,
            old_imported: 1,
            new_total: 2,
            new_ready: 0,
            new_success: 1,
            new_failed: 0,
            new_connection: 0,
        },
    }).as('importSummary');
}

export function mockUpdateAccountLink(): void {
    cy.intercept('POST', '**/accountlink/update/', {
        statusCode: 200,
        body: { type: 'success' },
    }).as('updateAccountLink');
}
