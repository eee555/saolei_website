// 个人主页
import 'cypress-if';
import { binaryStringToUint8Array } from '../support/stupidCypress';

const USER_ID = 2418 as const;
const USERNAME = 'testUser' as const;
const PASSWORD = 'testPassword' as const;
const REALNAME = 'testName' as const;

describe('Personal Profile', () => {
    it('Before All', () => {
        // 初始化数据库
        cy.flushDatabase();

        // 注册并登录用户
        cy.register(USER_ID, USERNAME, 'test@email.com', PASSWORD);
        cy.login(USERNAME, PASSWORD);
    });

    it('Profile section', () => {
        cy.visitUser(USER_ID);

        cy.get('.profile').contains(USERNAME);
        cy.get('.profile').contains(`#${USER_ID}`);
        cy.get('.profile').contains('匿名');

        cy.get('.avatar').find('img').should('have.attr', 'src').should('include', 'person.png');
    });

    it('Navigation', () => {
        cy.login(USERNAME, PASSWORD);
        cy.visitUser(USER_ID);
        cy.url().should('eq', `http://localhost:8080/#/player/${USER_ID}/summary`);

        cy.get('div.el-tabs__item').contains('纪录').click();
        cy.url().should('eq', `http://localhost:8080/#/player/${USER_ID}/record`);

        cy.get('div.el-tabs__item').contains('账号关联').click();
        cy.url().should('eq', `http://localhost:8080/#/player/${USER_ID}/accountlink`);

        cy.get('div.el-tabs__item').contains('录像').click();
        cy.url().should('eq', `http://localhost:8080/#/player/${USER_ID}/videos`);

        cy.get('div.el-tabs__item').contains('上传').click();
        cy.url().should('eq', `http://localhost:8080/#/player/${USER_ID}/upload`);
    });

    it('Cannot upload videos without real name', () => {
        cy.login(USERNAME, PASSWORD);
        cy.visitUser(USER_ID);
        cy.get('div.el-tabs__item').contains('上传').click();
        cy.contains('请修改为实名');
    });

    it('Change local name', () => {
        cy.login(USERNAME, PASSWORD);
        cy.visitUser(USER_ID);

        cy.get('.profile-section').contains('编辑信息').click();

        cy.get('.el-dialog').then((dialog) => {
            cy.wrap(dialog).contains('本名').parent().next().find('input').type(REALNAME);
            cy.wrap(dialog).find('button').contains('保存').click();
        });

        cy.get('.el-dialog').should('not.be.visible');
        cy.get('.profile').contains(REALNAME);
    });

    it('Upload video', function () {
        cy.login(USERNAME, PASSWORD);
        cy.visitUser(USER_ID, 'upload');

        // 准备录像文件
        cy.fixture('Exp_FL_35.09_3BV=132_3BVs=3.76_Pu Tian Yi(Hu Bei).avf', 'binary').then((fileContent) => {
            cy.wrap(binaryStringToUint8Array(fileContent)).as('videoFileExpAvf');
        });
        cy.fixture('3819-Time-1616-NF-9469-32-20151031.rmv', 'binary').then((fileContent) => {
            cy.wrap(binaryStringToUint8Array(fileContent)).as('videoFileIntRmv');
        });

        cy.get('.el-tabs__content').find('input[type=file]').selectFile([
            {
                contents: '@videoFileExpAvf',
                fileName: 'videoFileExp.avf',
            },
            {
                contents: '@videoFileIntRmv',
                fileName: 'videoFileInt.rmv',
            },
        ], { force: true });

        const expectedData = {
            ExpAvf: { '': '', Bv: '132', Bvs: '3.762', 状态: '新标识', 用时: '35.090', 级别: '高级', 结束时间: '2023-10-05 21:25:57' },
            IntRmv: { '': '', Bv: '32', Bvs: '3.379', 状态: '新标识', 用时: '9.469', 级别: '中级', 结束时间: '2015-10-31 22:53:35' },
        };

        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData.length).to.equal(2);
            expect(tableData[0]).to.deep.equal(expectedData.ExpAvf);
            expect(tableData[1]).to.deep.equal(expectedData.IntRmv);
        });

        cy.get('table:visible').find('.el-checkbox__input').first().click(); // 全选
        cy.get('button').contains(/^\s*上传\s*$/).click();
        cy.get('.el-loading-spinner').should('exist');
        cy.get('.el-loading-spinner').should('not.exist');

        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData.length).to.equal(2);
            expect(tableData[0]).to.deep.equal({ ...expectedData.ExpAvf, 状态: '上传成功' });
            expect(tableData[1]).to.deep.equal({ ...expectedData.IntRmv, 状态: '上传成功' });
        });
    });

    it('Cannot update avatar before sub200', () => {
        cy.login(USERNAME, PASSWORD);
        cy.visitUser(USER_ID);

        cy.get('.avatar').find('img').should('have.attr', 'title', '高级sub200后才可以修改头像');
    });

    it('Cannot update signature before sub200', () => {
        cy.login(USERNAME, PASSWORD);
        cy.visitUser(USER_ID);

        cy.get('.profile-section').contains('编辑信息').click();

        cy.get('.el-dialog').then((dialog) => {
            cy.wrap(dialog).contains('个性签名').parent().next().find('textarea').should('be.disabled');
            cy.wrap(dialog).contains('高级sub200后才可以修改个性签名');
        });
    });

    it('Add identifier', () => {
        cy.login(USERNAME, PASSWORD);
        cy.visitUser(USER_ID, 'summary');

        cy.contains('扫雷标识').next().next().find('table').then((table) => {
            cy.wrap(table).find('input').type('Pu Tian Yi(Hu Bei)');
            cy.wrap(table).find('.pi-plus').click();
        });

        cy.contains('添加标识成功');
        cy.closeElNotifications();
    });

    it('Auto load videos and identifiers when visiting summary', () => {
        cy.visitUser(USER_ID);

        cy.contains('共2个录像'); // calendar
        cy.contains('共1个Bv'); // bv

        cy.contains('扫雷标识').next().next().find('table').contains('Pu Tian Yi(Hu Bei)');
    });

    it('Auto load videos when visiting videos', () => {
        cy.visitUser(USER_ID, 'videos');

        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData.length).to.equal(2);
        });
    });

    it('Update avatar', () => {
        cy.login(USERNAME, PASSWORD);
        cy.visitUser(USER_ID);

        cy.get('.avatar').find('img').should('have.attr', 'title', '点击修改头像（剩余2次）');

        cy.get('.avatar').find('input[type=file]').selectFile('cypress/fixtures/test.png', { force: true });

        cy.get('.avatar').find('img').should('have.attr', 'src').and('include', `${USER_ID}?v=1`);

        cy.get('.avatar').find('img').should('have.attr', 'title', '点击修改头像（剩余1次）');
    });

    it('Update signature', () => {
        cy.login(USERNAME, PASSWORD);
        cy.visitUser(USER_ID);

        cy.get('.profile-section').contains('编辑信息').click();

        cy.get('.el-dialog').then((dialog) => {
            cy.wrap(dialog).contains('个性签名').parent().next().find('textarea').type('testSignature');
            cy.wrap(dialog).find('button').contains('保存').click();
        });

        cy.get('.el-dialog').should('not.be.visible');
        cy.get('.profile-section').contains('testSignature');
    });

    it('Guest view', () => {
        cy.visitUser(USER_ID);

        cy.get('div.el-tabs__item').contains('上传').should('not.exist');
        cy.get('.profile-section').contains('编辑信息').should('not.exist');

        cy.contains('扫雷标识').next().next().find('table').then((table) => {
            cy.wrap(table).find('input').should('not.exist');
        });
    });

    it('Navigate from homepage', () => {
        cy.visit('/');

        cy.get('.el-tabs').eq(1).contains(REALNAME).click();

        cy.contains('我的空间').click();

        cy.url().should('eq', `http://localhost:8080/#/player/${USER_ID}/summary`);

        cy.contains('共2个录像');
    });
});
