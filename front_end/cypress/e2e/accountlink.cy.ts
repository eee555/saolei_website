
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
    'wom': {
        platform: 'Minesweeper.Online',
        identifier: '1782682',
    },
    'saolei': {
        platform: '扫雷网',
        identifier: '18290',
    },
    'msgames': {
        platform: 'Authoritative Minesweeper',
        identifier: '7872',
    },
    'qq': {
        platform: '腾讯QQ',
        identifier: '123456789',
    },
} as const;

function linkNewAccount(platform: string, identifier: string) {
    cy.contains('账号关联').next().find('.pi-plus').click();
    cy.contains('添加关联账号');
    cy.get('.el-dialog__body').within(() => {
        cy.contains('平台').next().contains('Select').click();
    });
    cy.get('li').contains(platform).click();
    cy.get('.el-dialog__body').within(() => {
        cy.contains('ID').next().find('input').type(identifier);
        cy.contains('确认').click();
    });
    cy.get('.el-dialog__body').should('not.be.visible');
}

function expectUnverifiedAccount(index: number, platform: string, identifier: string) {
    cy.contains('账号关联').next().children().filter(':visible').eq(index).within(() => {
        cy.contains(platform);
        cy.contains(`#${identifier}`);
        cy.contains('账号未验证');
    });
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
        cy.visitUser(USER.id);
        cy.contains('账号关联').should('not.exist');
    });

    it('Link Public Accounts', () => {
        cy.viewport(1000, 2000);
        cy.login(USER.username, USER.password);
        cy.visitUser(USER.id);

        linkNewAccount(LINKS.wom.platform, LINKS.wom.identifier);
        expectUnverifiedAccount(0, LINKS.wom.platform, LINKS.wom.identifier);

        linkNewAccount(LINKS.saolei.platform, LINKS.saolei.identifier);
        expectUnverifiedAccount(1, LINKS.saolei.platform, LINKS.saolei.identifier);

        linkNewAccount(LINKS.msgames.platform, LINKS.msgames.identifier);
        expectUnverifiedAccount(2, LINKS.msgames.platform, LINKS.msgames.identifier);
    });

    it('Guest View - Should Not See Unverified Accounts', () => {
        cy.visitUser(USER.id);
        cy.contains('账号关联').should('not.exist');
    });

    it('Staff View - Should Not See The Add Button', () => {
        cy.login(STAFF.username, STAFF.password);
        cy.visitUser(USER.id);
        cy.contains('账号关联').next().find('.pi-plus').should('not.exist');
    });

    it('Link Private Accounts', () => {
        cy.login(USER.username, USER.password);
        cy.visitUser(USER.id);

        linkNewAccount(LINKS.qq.platform, LINKS.qq.identifier);
        expectUnverifiedAccount(3, LINKS.qq.platform, LINKS.qq.identifier);

        cy.contains('账号关联').next().find('.pi-plus').should('not.exist');
    });

    it('Guest View - Should Not See Private Accounts', () => {
        cy.visitUser(USER.id);
        cy.contains('账号关联').next().children().should('have.length', 3);
    });

    it('Verify Saolei Account', () => {
        // 登录管理员账号进行验证
        cy.login(STAFF.username, STAFF.password);
        cy.visit('/#/staff');
        cy.contains('账号绑定').click();

        cy.contains('ID').next().find('input').type(`${USER.id}{enter}`);
        cy.contains('平台').next().contains('Select').click();
        cy.get('li').contains(LINKS.wom.platform).click();
    });
});

export {};
