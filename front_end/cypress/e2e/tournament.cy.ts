const HOST = {
    id: 10,
    username: 'tournament_host',
    realname: 'Tournament Host',
} as const;

interface DangerzoneTournament {
    id: number;
    subclass: 'g';
    state: string;
    start_time: string;
    end_time: string;
    host_id: number;
    data: {
        order: number;
        token: string;
    };
}

function createTournament(order: number, state: string) {
    return cy.dangerzonePost<DangerzoneTournament>('create_gsc_tournament', {
        order,
        state,
        start_time: '2000-01-01T00:00:00+08:00',
        end_time: '2099-01-01T00:00:00+08:00',
        token: `G${order.toString().padStart(5, '0')}`,
        host_id: HOST.id,
    });
}

function assertVisibleTournamentNames(expectedNames: string[]) {
    cy.get('.el-table:visible').first().within(() => {
        expectedNames.forEach((name) => {
            cy.contains('.el-table__row', name).should('be.visible');
        });
        cy.get('.el-table__row').should((rows) => {
            const names = [...rows].map((row) => row.textContent ?? '');
            expect(names).to.have.length(expectedNames.length);
            expectedNames.forEach((name) => {
                expect(names.some((rowText) => rowText.includes(name))).to.equal(true);
            });
        });
    });
}

describe('Tournament page tabs backed by real API data', () => {
    beforeEach(() => {
        cy.flushDatabase();
        cy.clearLocalStorage();
        cy.registerUser(HOST);
        createTournament(21, 'n').as('normalTournament');
        createTournament(22, 'a').as('awardedTournament');
        createTournament(23, 'p').as('pendingTournament');
        createTournament(24, 'c').as('cancelledTournament');
    });

    it('loads each homepage category tab from the backend', () => {
        cy.visit('/#/tournament/');

        cy.contains('.el-tabs__item.is-active', '正常').should('be.visible');
        assertVisibleTournamentNames(['第21届金羊杯']);

        cy.contains('.el-tabs__item', '已颁奖').click();
        assertVisibleTournamentNames(['第22届金羊杯']);

        cy.contains('.el-tabs__item', '其他').click();
        assertVisibleTournamentNames(['第23届金羊杯', '第24届金羊杯']);

        cy.contains('.el-tabs__item', '全部').click();
        assertVisibleTournamentNames(['第21届金羊杯', '第22届金羊杯', '第23届金羊杯', '第24届金羊杯']);
    });

    it('keeps tournament detail tabs and the router in sync', () => {
        cy.get<Cypress.Response<DangerzoneTournament>>('@normalTournament').then((response) => {
            const { id, data } = response.body;
            cy.visit('/#/tournament/');
            cy.contains('.el-table__row', `第${data.order}届金羊杯`).click();

            cy.location('hash').should('eq', `#/tournament/${id}`);
            cy.contains('h1', `第${data.order}届金羊杯`).should('be.visible');
            cy.contains('.el-tabs__item', '比赛首页').should('be.visible');

            cy.contains('.el-tabs__item', '比赛首页').click();
            cy.location('hash').should('eq', '#/tournament');

            cy.contains('.el-tabs__item', `第${data.order}届金羊杯`).click();
            cy.location('hash').should('eq', `#/tournament/${id}`);
        });
    });
});

export {};
