const USER = { id: 37891, username: 'arbiterCsvUser', email: 'arbiter-csv@example.com', password: 'arbiterCsvPassword' };
const AVF = 'cypress/fixtures/Exp_FL_35.09_3BV=132_3BVs=3.76_Pu Tian Yi(Hu Bei).avf';

describe('Arbiter CSV with uploaded videos', () => {
    before(() => {
        cy.flushDatabase();
        cy.registerUser(USER);
    });

    it('shows a local row, uploads its AVF and replaces it with the real server row', () => {
        cy.login(USER.username, USER.password);
        cy.request({ method: 'POST', url: 'http://127.0.0.1:8000/api/userprofile/update_profile', form: true, body: { realname: 'CSV测试' } });
        cy.intercept('GET', '**/api/userprofile/videolist*').as('videos');
        cy.visitUser(USER.id, 'videos');
        cy.wait('@videos').its('response.body').should('have.length', 0);
        cy.get('[data-cy=toggle-arbiter-csv]').should('contain.text', '导入CSV').click();
        cy.get('[data-cy=arbiter-csv-upload] input[type=file]').should('be.enabled').selectFile('cypress/fixtures/stats_csv.csv', { force: true });
        cy.get('[data-cy=arbiter-csv-result]').should('contain.text', '1 个本机未上传录像');
        cy.get('table:visible').should('contain.text', '35.090');
        cy.get('[data-cy=local-video-state]').should('have.length', 1);

        cy.window().then((win) => {
            win.location.hash = `#/player/${USER.id}/upload`;
        });
        cy.get('.el-tabs__content input[type=file]').should('not.be.disabled').selectFile(AVF, { force: true });
        cy.get('table:visible').should('contain.text', '35.090');
        cy.get('table:visible .checkbox-input').first().check();
        cy.contains('button', /^\s*上传\s*$/).click();
        cy.get('table:visible').should('contain.text', '新标识');
        cy.closeElNotifications();

        cy.window().then((win) => {
            win.location.hash = `#/player/${USER.id}/videos`;
        });
        cy.wait('@videos').its('response.body').should((videos: { state: string; timems: number }[]) => {
            expect(videos).to.have.length(1);
            expect(videos[0]).to.include({ timems: 35090, state: 'd' });
        });
        cy.get('[data-cy=arbiter-csv-result]').should('contain.text', '0 个本机未上传录像');
        cy.get('[data-cy=local-video-state]').should('not.exist');
        cy.get('table:visible').getTable().should('have.length', 1);
        cy.get('table:visible').should('contain.text', '35.090');
    });
});

export {};
