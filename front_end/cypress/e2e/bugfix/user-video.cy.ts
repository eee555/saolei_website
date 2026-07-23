const USER = {
    id: 36987,
    username: 'repeatVisitor',
    email: 'repeatVisitor@email.com',
    password: 'repeatVisitorPassword',
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

describe('User Videos', () => {
    it('Before All', () => {
        cy.flushDatabase();
        cy.register(USER.id, USER.username, USER.email, USER.password);
        createVideo(31000);
    });

    it('Reloads the video list when revisiting the same own user page', () => {
        cy.login(USER.username, USER.password);
        cy.visit('/#/settings');
        cy.contains(USER.username).should('be.visible');

        navigateHash(`#/player/${USER.id}/videos`);
        cy.get('.p-datatable').should('contain', '31.000');
        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData.length).to.equal(1);
        });

        createVideo(22000);

        navigateHash('#/settings');
        navigateHash(`#/player/${USER.id}/videos`);
        cy.get('.p-datatable').should('contain', '22.000');
        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData.length).to.equal(2);
        });
    });
});

export {};
