
const STAFF = {
    id: 1,
    username: 'staff',
    email: 'staff@email.com',
    password: 'staffPassword',
} as const;
const USER = {
    id: 2,
    username: 'user',
    email: 'user@email.com',
    password: 'userPassword',
} as const;
const LINKS = {
    bilibili: {
        platform: '哔哩哔哩',
        identifier: '208259',
    },
    wom: {
        platform: 'Minesweeper.Online',
        identifier: '1782682',
    },
    saolei: {
        platform: '扫雷网',
        identifier: '18290',
    },
    msgames: {
        platform: '国际网',
        identifier: '7872',
    },
    qq: {
        platform: '腾讯QQ',
        identifier: '123456789',
    },
} as const;

function linkNewAccount(platform: string, identifier: string) {
    cy.intercept('POST', '/api/accountlink/create/').as('addAccountLink');
    cy.get('.account-link-main').find('.pi-plus').click();
    cy.contains('添加关联账号');
    cy.get('.el-dialog__body').within(() => {
        cy.contains('平台').next().contains('Select').click();
    });
    cy.get('li').contains(platform).click();
    if (platform === LINKS.bilibili.platform) {
        cy.contains('隐私提醒');
        cy.contains('关联 Bilibili 后');
    }
    cy.get('.el-dialog__body').contains('ID').next().find('input').type(identifier);
    cy.get('.el-dialog__footer').contains('确认').click();
    cy.wait('@addAccountLink').its('response.statusCode').should('eq', 200);
    cy.get('.el-dialog__body:visible').should('not.exist');
}

function expectUnverifiedAccount(platform: string, identifier: string) {
    cy.contains('.account-link-main > :visible', `#${identifier}`).within(() => {
        cy.contains(platform);
        cy.contains(`#${identifier}`);
        cy.contains('账号未验证');
    });
}

function visitStaffAccountLink() {
    cy.login(STAFF.username, STAFF.password);
    cy.intercept('GET', '/api/accountlink/admin/queue').as('accountLinkQueue');
    cy.visit('/#/staff/accountlink');
    cy.wait('@accountLinkQueue');
}

function expectAccountLinkTableRow(platform: string, identifier: string, verified: boolean) {
    cy.get('table:visible').getTable().should((tableData) => {
        const row = tableData.find((item) => item['Platform ID'] === identifier);

        expect(row).to.deep.equal({
            'User ID': `${USER.id}`,
            Platform: platform,
            'Platform ID': identifier,
            Verified: `${verified}`,
        });
    });
}

function expectAccountLinkTableData(expected: { platform: string; identifier: string; verified: boolean }[]) {
    cy.get('table:visible').getTable().should((tableData) => {
        expect(tableData.length).to.equal(expected.length);
        expected.forEach((item) => {
            const row = tableData.find((tableRow) => tableRow['Platform ID'] === item.identifier);
            expect(row).to.deep.equal({
                'User ID': `${USER.id}`,
                Platform: item.platform,
                'Platform ID': item.identifier,
                Verified: `${item.verified}`,
            });
        });
    });
}

function staffVerifyAccount(platform: string, identifier: string) {
    visitStaffAccountLink();
    expectAccountLinkTableRow(platform, identifier, false);

    cy.contains(':visible', 'ID').first().next().find('input').type(`${USER.id}{enter}`);
    cy.contains('平台').next().contains('Select').click();
    cy.get('li').contains(platform).click();
    cy.contains('平台ID').next().find('input').type(`${identifier}{enter}`);
    cy.contains(/^\s*绑定\s*$/).click();
    cy.wait('@accountLinkQueue');

    expectAccountLinkTableRow(platform, identifier, true);
}

describe('Account Link', () => {
    it('Before All', () => {
        // 初始化数据库
        cy.flushDatabase();

        // 注册用户
        cy.register(STAFF.id, STAFF.username, STAFF.email, STAFF.password);
        cy.setStaff(STAFF.id);
        cy.register(USER.id, USER.username, USER.email, USER.password);
    });

    it('Guest View - No Account Links', () => {
        cy.visitUser(USER.id, 'accountlink');
        cy.get('.account-link-main').children().should('not.exist');
    });

    it('Link Public Accounts', () => {
        cy.login(USER.username, USER.password);
        cy.visitUser(USER.id, 'accountlink');

        linkNewAccount(LINKS.wom.platform, LINKS.wom.identifier);
        expectUnverifiedAccount(LINKS.wom.platform, LINKS.wom.identifier);

        linkNewAccount(LINKS.saolei.platform, LINKS.saolei.identifier);
        expectUnverifiedAccount(LINKS.saolei.platform, LINKS.saolei.identifier);

        linkNewAccount(LINKS.msgames.platform, LINKS.msgames.identifier);
        expectUnverifiedAccount(LINKS.msgames.platform, LINKS.msgames.identifier);

        linkNewAccount(LINKS.bilibili.platform, LINKS.bilibili.identifier);
        expectUnverifiedAccount(LINKS.bilibili.platform, LINKS.bilibili.identifier);
    });

    it('Guest View - Should Not See Unverified Accounts', () => {
        cy.visitUser(USER.id, 'accountlink');
        cy.get('.account-link-main').children().should('not.exist');
    });

    it('Staff View - Should Not See The Add Button', () => {
        cy.login(STAFF.username, STAFF.password);
        cy.visitUser(USER.id, 'accountlink');
        cy.get('.account-link-main').find('.pi-plus').should('not.exist');
    });

    it('Link Private Accounts', () => {
        cy.login(USER.username, USER.password);
        cy.visitUser(USER.id, 'accountlink');

        linkNewAccount(LINKS.qq.platform, LINKS.qq.identifier);

        cy.get('.account-link-main').find('.pi-plus').should('not.exist');
    });

    it('Staff View - Should Render Account Link Table', () => {
        visitStaffAccountLink();

        expectAccountLinkTableData([
            { platform: LINKS.wom.platform, identifier: LINKS.wom.identifier, verified: false },
            { platform: LINKS.saolei.platform, identifier: LINKS.saolei.identifier, verified: false },
            { platform: LINKS.msgames.platform, identifier: LINKS.msgames.identifier, verified: false },
            { platform: LINKS.bilibili.platform, identifier: LINKS.bilibili.identifier, verified: false },
            { platform: LINKS.qq.platform, identifier: LINKS.qq.identifier, verified: false },
        ]);
    });

    it('Verify WoM Account', () => {
        staffVerifyAccount(LINKS.wom.platform, LINKS.wom.identifier);
    });

    it('Verify Saolei Account', () => {
        staffVerifyAccount(LINKS.saolei.platform, LINKS.saolei.identifier);
    });

    it('Verify MSGames Account', () => {
        staffVerifyAccount(LINKS.msgames.platform, LINKS.msgames.identifier);
    });

    it('Verify Bilibili Account', () => {
        staffVerifyAccount(LINKS.bilibili.platform, LINKS.bilibili.identifier);
    });

    it('Guest View - Should Not See Private Accounts', () => {
        cy.visitUser(USER.id, 'accountlink');
        cy.get('.account-link-main').children().filter(':visible').should('have.length', 4);
        cy.get('.account-link-main').children().filter(':visible').should(($cards) => {
            const cardTexts = [...$cards].map((card) => card.textContent);

            expect(cardTexts[0]).to.contain(`${LINKS.saolei.platform}\u00a0#${LINKS.saolei.identifier}`);
            expect(cardTexts[1]).to.contain(`${LINKS.msgames.platform}\u00a0#${LINKS.msgames.identifier}`);
            expect(cardTexts[2]).to.contain(`${LINKS.wom.platform}\u00a0#${LINKS.wom.identifier}`);
            expect(cardTexts[3]).to.contain(`${LINKS.bilibili.platform}\u00a0#${LINKS.bilibili.identifier}`);
        });
    });
});

export {};
