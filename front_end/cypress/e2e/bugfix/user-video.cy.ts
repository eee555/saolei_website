const USER = {
    id: 36987,
    username: 'user',
    email: 'user@email.com',
    password: 'userPassword',
} as const;

function createVideo(timems: number) {
    return cy.request({
        method: 'POST',
        url: 'http://127.0.0.1:8000/dangerzone/create_video',
        body: {
            user_id: USER.id,
            timems,
            bv: 100,
        },
    }).then((response) => {
        expect(response.status).to.equal(200);
    });
}

function navigateHash(hash: string) {
    cy.window().then((win) => {
        win.location.hash = hash;
    });
    cy.location('hash').should('eq', hash);
}

function navigateToUserTab(tab: string) {
    navigateHash(`#/player/${USER.id}/${tab}`);
    cy.get('.personal-homepage').should('be.visible');
    cy.get('.personal-homepage .el-tabs__item.is-active').should('have.attr', 'aria-controls', `pane-${tab}`);
}

function navigateAwayFromUserPage() {
    navigateHash('#/settings');
    cy.get('.personal-homepage').should('not.exist');
}

function waitForVideoList(count: number) {
    cy.wait('@getUserVideos').its('response.body').should((videos) => {
        expect(videos).to.have.length(count);
    });
}

describe('User Videos', () => {
    it('Before All', () => {
        cy.flushDatabase();
        cy.registerUser(USER);
        createVideo(31000);
    });

    it('Reuses cached own videos across navigation and loads external changes on explicit refresh', () => {
        let videoListRequestCount = 0;
        cy.intercept({ method: 'GET', pathname: '/api/userprofile/videolist' }, (request) => {
            videoListRequestCount += 1;
            request.continue();
        }).as('getUserVideos');
        cy.login(USER.username, USER.password);

        cy.visitUser(USER.id, 'videos');
        waitForVideoList(1);
        cy.wrap(null).should(() => {
            expect(videoListRequestCount).to.equal(1);
        });
        cy.contains(USER.username).should('be.visible');
        cy.get('table:visible').should('contain', '31.000');
        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData.length).to.equal(1);
        });

        // External changes do not invalidate this page's cache; UI uploads invalidate profile data.
        createVideo(22000);

        navigateToUserTab('top');
        cy.get('[data-cy=pb-grid-e]').should('be.visible');
        cy.wrap(null).should(() => {
            expect(videoListRequestCount).to.equal(1);
        });
        navigateToUserTab('videos');
        cy.wrap(null).should(() => {
            expect(videoListRequestCount).to.equal(1);
        });
        cy.get('table:visible').should('not.contain', '22.000');
        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData.length).to.equal(1);
        });

        navigateAwayFromUserPage();
        navigateToUserTab('videos');
        cy.get('table:visible').should('not.contain', '22.000');
        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData.length).to.equal(1);
        });
        cy.wrap(null).should(() => {
            expect(videoListRequestCount).to.equal(1);
        });

        cy.get('[data-cy=refresh-videos]').should('be.enabled').click();
        waitForVideoList(2);
        cy.wrap(null).should(() => {
            expect(videoListRequestCount).to.equal(2);
        });
        cy.get('table:visible').should('contain', '22.000');
        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData.length).to.equal(2);
        });
    });
});

export {};
