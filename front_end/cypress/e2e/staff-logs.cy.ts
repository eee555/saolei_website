const STAFF = {
    id: 1,
    username: 'staff',
    email: 'staff@email.com',
    password: 'staffPassword',
} as const;

const LOG_FILE = 'cypress-staff-log.log';
const LOG_CONTENT = [
    'cypress staff log start',
    'admin can read log tail',
    'cypress staff log end',
].join('\n');
const TAIL_UPDATE = '\nrealtime tail update from cypress';

function writeLog(filename: string, content: string, append = false) {
    cy.request({
        method: 'POST',
        url: 'http://127.0.0.1:8000/dangerzone/write_log',
        body: {
            filename,
            content,
            append,
        },
    }).then((response) => {
        expect(response.status).to.eq(200);
    });
}

describe('Staff logs', () => {
    beforeEach(() => {
        void Cypress.session.clearAllSavedSessions();
        cy.flushDatabase();
        cy.register(STAFF.id, STAFF.username, STAFF.email, STAFF.password);
        cy.setStaff(STAFF.id);
        writeLog(LOG_FILE, LOG_CONTENT);
    });

    it('lets an administrator view a log file', () => {
        cy.login(STAFF.username, STAFF.password);
        cy.intercept('GET', '/api/common/staff/logs').as('listLogs');
        cy.intercept('GET', '/api/common/staff/logtail*').as('logTail');

        cy.visit('/#/staff/logs');
        cy.wait('@listLogs');

        cy.contains('.el-table__row', LOG_FILE).within(() => {
            cy.contains('button', '查看').click();
        });
        cy.wait('@logTail').its('response.statusCode').should('eq', 200);

        cy.contains('.log-toolbar', LOG_FILE);
        cy.get('.log-viewer').should('contain', 'cypress staff log start');
        cy.get('.log-viewer').should('contain', 'admin can read log tail');
        cy.get('.log-viewer').should('contain', 'cypress staff log end');
        cy.contains('.log-toolbar', '实时更新中', { timeout: 10000 });

        writeLog(LOG_FILE, TAIL_UPDATE, true);
        cy.get('.log-viewer', { timeout: 15000 }).should('contain', TAIL_UPDATE.trim());
    });
});
