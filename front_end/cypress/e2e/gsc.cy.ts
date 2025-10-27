// 金羊杯

const HOST = {
    id: 48,
    username: 'gscHost',
    email: 'gscHost@email.com',
    password: 'gscHostPassword',
    realname: '匿名',
} as const;
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

function visitGSCAdmin(gscID: number) {
    cy.visit('/#/gsc/admin/');
    cy.contains('第').next().find('input').invoke('val', '');
    cy.contains('第').next().find('input').type(`${gscID}{enter}`);
}

function setDateTime(dateStr: string, timeStr: string) {
    cy.get('[placeholder="Select date"]').filter(':visible').type(`${dateStr}{enter}`);
    cy.get('[placeholder="Select time"]').filter(':visible').invoke('val', '');
    cy.get('[placeholder="Select time"]').filter(':visible').type(`${timeStr}{enter}`);
    cy.get('button:visible').contains('OK').click();
}

function setStartDateTime(dateStr: string, timeStr: string) {
    cy.contains('设置开始时间：').next().click();
    setDateTime(dateStr, timeStr);
    cy.contains('操作成功');
    cy.closeElNotifications();
}

function setEndDateTime(dateStr: string, timeStr: string) {
    cy.contains('设置结束时间：').next().click();
    setDateTime(dateStr, timeStr);
    cy.contains('操作成功');
    cy.closeElNotifications();
}

describe('GSC', () => {
    it('Before All', () => {
        // 初始化数据库
        cy.flushDatabase();

        // 注册用户
        cy.register(HOST.id, HOST.username, HOST.email, HOST.password);
        cy.register(STAFF.id, STAFF.username, STAFF.email, STAFF.password);
        cy.register(USER.id, USER.username, USER.email, USER.password);
    });

    it('Create GSC', () => {
        // 主办方创建比赛
        cy.login(HOST.username, HOST.password);
        cy.visit('/#/gsc/admin/');

        cy.contains('请输入非零届数');
        cy.contains('第').next().find('input').type('2{enter}');
        cy.contains('未找到该届信息');
        cy.contains('创建比赛').click();
        cy.contains('操作成功');
        cy.closeElNotifications();

        cy.contains('开始时间：未设置');
        cy.contains('结束时间：未设置');
        cy.contains('标识：未设置');

        cy.visit('/#/tournament/');
        cy.contains('第2届金羊杯');
        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData[0].状态).to.equal('审核中');
            expect(tableData[0].比赛).to.equal('第2届金羊杯');
            expect(tableData[0].主办方).to.equal(HOST.realname);
            expect(tableData[0].开始时间).to.equal('未定');
            expect(tableData[0].结束时间).to.equal('未定');
        });
    });

    it('Set start time', () => {
        cy.login(HOST.username, HOST.password);
        visitGSCAdmin(2);

        cy.contains('开始时间：未设置');
        setStartDateTime('2100-01-01', '00:00:00');
        cy.contains('开始时间：2100-01-01 00:00:00');

        cy.visit('/#/tournament/');
        cy.contains('第2届金羊杯');
        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData[0].开始时间).to.equal('2100-01-01 00:00:00');
        });
    });

    it('Set end time', () => {
        cy.login(HOST.username, HOST.password);
        visitGSCAdmin(2);

        cy.contains('结束时间：未设置');
        setEndDateTime('2100-01-02', '00:00:00');
        cy.contains('结束时间：2100-01-02 00:00:00');

        cy.visit('/#/tournament/');
        cy.contains('第2届金羊杯');
        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData[0].结束时间).to.equal('2100-01-02 00:00:00');
        });
    });

    it('Reset start time', () => {
        cy.login(HOST.username, HOST.password);

        visitGSCAdmin(2);
        cy.contains('开始时间：2100-01-01 00:00:00');
        setStartDateTime('2099-12-31', '00:00:00');
        cy.contains('开始时间：2099-12-31 00:00:00');

        cy.visit('/#/tournament/');
        cy.contains('第2届金羊杯');
        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData[0].开始时间).to.equal('2099-12-31 00:00:00');
        });
    });

    it('Reset end time', () => {
        cy.login(HOST.username, HOST.password);
        visitGSCAdmin(2);
        cy.contains('结束时间：2100-01-02 00:00:00');
        setEndDateTime('2100-01-03', '00:00:00');
        cy.contains('结束时间：2100-01-03 00:00:00');

        cy.visit('/#/tournament/');
        cy.contains('第2届金羊杯');
        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData[0].结束时间).to.equal('2100-01-03 00:00:00');
        });
    });

    it('Create more GSC for tests', () => {
        // 进行中
        cy.login(HOST.username, HOST.password);
        visitGSCAdmin(3);
        cy.contains('创建比赛').click();
        cy.contains('操作成功');
        cy.closeElNotifications();

        setStartDateTime('2000-01-01', '00:00:00');
        setEndDateTime('2100-01-01', '00:00:00');

        // 已结束
        visitGSCAdmin(4);
        cy.contains('创建比赛').click();
        cy.contains('操作成功');
        cy.closeElNotifications();
        setStartDateTime('2000-01-01', '00:00:00');
        setEndDateTime('2000-01-02', '00:00:00');

        // 比赛页
        cy.visit('/#/tournament/');
        cy.contains('第2届金羊杯');
        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData[0].状态).to.equal('审核中');
            expect(tableData[1].状态).to.equal('审核中');
            expect(tableData[2].状态).to.equal('审核中');

            expect(tableData[0].比赛).to.equal('第2届金羊杯');
            expect(tableData[1].比赛).to.equal('第3届金羊杯');
            expect(tableData[2].比赛).to.equal('第4届金羊杯');

            expect(tableData[0].主办方).to.equal(HOST.realname);
            expect(tableData[1].主办方).to.equal(HOST.realname);
            expect(tableData[2].主办方).to.equal(HOST.realname);

            expect(tableData[0].开始时间).to.equal('2099-12-31 00:00:00');
            expect(tableData[1].开始时间).to.equal('2000-01-01 00:00:00');
            expect(tableData[2].开始时间).to.equal('2000-01-01 00:00:00');

            expect(tableData[0].结束时间).to.equal('2100-01-03 00:00:00');
            expect(tableData[1].结束时间).to.equal('2100-01-01 00:00:00');
            expect(tableData[2].结束时间).to.equal('2000-01-02 00:00:00');
        });
    });

    it('Admin validate', () => {
        cy.login(STAFF.username, STAFF.password);
        cy.visit('/#/staff/');
        cy.contains('比赛管理').click();
    });
});
