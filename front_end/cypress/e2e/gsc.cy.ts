// 金羊杯
const ArbiterIcon = '/img/ms_arbiter_MAINICON.ico';
const MetasweeperIcon = '/src/assets/img/img_meta.png';

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

const GSC_TOKEN = 'G1234' as const;

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

function assertTableData(expected: Array<Record<string, any>>) {
    return cy.get('table:visible').getTable().should((tableData) => {
        expected.forEach((exp, i) => {
            Object.keys(exp).forEach((key) => {
                expect(tableData[i][key]).to.equal(exp[key]);
            });
        });
    });
}

describe('GSC', () => {
    it('Before All', () => {
        // 初始化数据库
        cy.flushDatabase();

        // 注册用户
        cy.register(HOST.id, HOST.username, HOST.email, HOST.password);
        cy.register(STAFF.id, STAFF.username, STAFF.email, STAFF.password);
        cy.setStaff(STAFF.id);
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
        assertTableData([
            { 状态: '审核中', 比赛: '第2届金羊杯', 主办方: HOST.realname, 开始时间: '2099-12-31 00:00:00', 结束时间: '2100-01-03 00:00:00' },
            { 状态: '审核中', 比赛: '第3届金羊杯', 主办方: HOST.realname, 开始时间: '2000-01-01 00:00:00', 结束时间: '2100-01-01 00:00:00' },
            { 状态: '审核中', 比赛: '第4届金羊杯', 主办方: HOST.realname, 开始时间: '2000-01-01 00:00:00', 结束时间: '2000-01-02 00:00:00' },
        ]);
    });

    it('Admin validate', () => {
        cy.login(STAFF.username, STAFF.password);
        cy.visit('/#/staff/');
        cy.contains('比赛管理').click();

        cy.contains('比赛ID').get('input').filter(':visible').clear();
        cy.contains('比赛ID').get('input').filter(':visible').type('1{enter}');
        cy.get('button').filter(':visible').contains('查询').click();
        cy.contains('第2届金羊杯');
        cy.contains('审核中');
        cy.get('.pi-times').click();
        cy.contains('已取消');

        cy.get('.pi-check').click();
        cy.contains('即将开始');

        cy.contains('比赛ID').get('input').filter(':visible').clear();
        cy.contains('比赛ID').get('input').filter(':visible').type('2{enter}');
        cy.get('button').filter(':visible').contains('查询').click();
        cy.contains('第3届金羊杯');
        cy.contains('审核中');
        cy.get('.pi-check').click();
        cy.contains('进行中');

        cy.contains('比赛ID').get('input').filter(':visible').clear();
        cy.contains('比赛ID').get('input').filter(':visible').type('3{enter}');
        cy.get('button').filter(':visible').contains('查询').click();
        cy.contains('第4届金羊杯');
        cy.contains('审核中');
        cy.get('.pi-check').click();
        cy.contains('结算中');
    });

    it('Tournament Page', () => {
        cy.visit('/#/tournament/');
        cy.contains('第2届金羊杯');
        assertTableData([
            { 状态: '即将开始', 比赛: '第2届金羊杯', 主办方: HOST.realname, 开始时间: '2099-12-31 00:00:00', 结束时间: '2100-01-03 00:00:00' },
            { 状态: '进行中', 比赛: '第3届金羊杯', 主办方: HOST.realname, 开始时间: '2000-01-01 00:00:00', 结束时间: '2100-01-01 00:00:00' },
            { 状态: '结算中', 比赛: '第4届金羊杯', 主办方: HOST.realname, 开始时间: '2000-01-01 00:00:00', 结束时间: '2000-01-02 00:00:00' },
        ]);
    });

    it('Generate and Modify Token', () => {
        cy.login(HOST.username, HOST.password);
        visitGSCAdmin(3);
        cy.contains('span', /^标识：G\d{5}$/).should('exist');
        cy.contains('设置标识：').next().find('input').type(`${GSC_TOKEN}{enter}`);
        cy.contains('修改').click();
        cy.contains('操作成功');
        cy.closeElNotifications();
        cy.contains('span', `标识：${GSC_TOKEN}`).should('exist');
    });

    it('Preparing Tournament', () => {
        cy.visit('/#/tournament/1');
        cy.contains('即将开始');
        cy.contains('如何参赛').next().within(() => {
            cy.get(`img[src="${MetasweeperIcon}"]`).click();
            cy.contains('比赛开始后会公布比赛标识。');

            cy.get(`img[src="${ArbiterIcon}"]`).click();
            cy.contains('比赛开始后在这里注册标识。');
        });

        cy.visit('/#/tournament/2');
        cy.contains('进行中');
    });

    it('Ongoing Tournament', () => {
        cy.visit('/#/tournament/2');
        cy.contains('进行中');
        cy.contains('如何参赛').next().within(() => {
            cy.get(`img[src="${MetasweeperIcon}"]`).click();
            cy.contains('在元扫雷中将比赛标识设置为');
            cy.contains(`${GSC_TOKEN}`);

            cy.get(`img[src="${ArbiterIcon}"]`).click();
            cy.contains('请在这里注册参赛标识。');
            cy.contains(`Guo Jin Yang ${GSC_TOKEN}`);
        });
        cy.contains('即时成绩');
    });

    it('Finished Tournament', () => {
        cy.visit('/#/tournament/3');
        cy.contains('结算中');
        cy.contains('如何参赛').should('not.exist');
        cy.contains('比赛结果');

        cy.login(STAFF.username, STAFF.password);
        cy.visit('/#/staff/');
        cy.contains('后台任务').click();

        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData[0].status).to.equal('READY');
            expect(tableData[0].args_kwargs.replace(/\s/g, '')).to.equal('{"args":[4],"kwargs":{}}');
            expect(tableData[0].task_path).to.equal('tournament.tasks.task_gsc_finish');
        });
    });
});

export {};
