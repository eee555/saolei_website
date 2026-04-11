// 个人主页
import 'cypress-if';
import { binaryStringToUint8Array } from '../support/stupidCypress';

const USER_ID = 2418 as const;



describe('Personal Profile', () => {
    it('Before All', () => {
        // 初始化数据库
        cy.flushDatabase();

        // 注册并登录用户
        cy.register(USER_ID, 'testUser', 'test@email.com', 'testPassword');
        cy.login('testUser', 'testPassword');
    });

    it('Guest view', () => {
        cy.visitUser(USER_ID);
        cy.contains('个人信息');
        cy.contains('个人纪录');
        cy.contains('全部录像');
        cy.contains('上传录像').should('not.exist');
    });

    it('Cannot upload videos without real name', () => {
        cy.login('testUser', 'testPassword');
        cy.visitUser(USER_ID);
        cy.contains('上传录像').click();
        cy.contains('请修改为实名');
    });

    it('Change real name', () => {
        cy.login('testUser', 'testPassword');
        cy.visitUser(USER_ID);
        cy.contains('修改简介').click();
        cy.contains('修改简介').if().should('not.be.visible');

        cy.contains('姓名').next().find('input').clear();
        cy.contains('姓名').next().find('input').type('testName');
        cy.contains('确认').click();

        cy.contains('修改简介').if().should('be.visible');
    });

    it('Parse video', function () {
        cy.login('testUser', 'testPassword');
        cy.visitUser(USER_ID);
        cy.contains('上传录像').click();

        // 准备录像文件
        cy.fixture('Exp_FL_35.09_3BV=132_3BVs=3.76_Pu Tian Yi(Hu Bei).avf', 'binary').then((fileContent) => {
            cy.wrap(binaryStringToUint8Array(fileContent)).as('videoFileExpAvf');
        });
        cy.fixture('4376-Custom-FL-30x24-860.360-357-226m-20220522.avf', 'binary').then((fileContent) => {
            cy.wrap(binaryStringToUint8Array(fileContent)).as('videoFileCusAvf');
        });
        cy.fixture('3819-Time-1616-NF-9469-32-20151031.rmv', 'binary').then((fileContent) => {
            cy.wrap(binaryStringToUint8Array(fileContent)).as('videoFileIntRmv');
        });

        cy.get('input[type=file]').selectFile([
            {
                contents: '@videoFileExpAvf',
                fileName: 'videoFileExp.avf',
            },
            {
                contents: '@videoFileCusAvf',
                fileName: 'videoFileCus.avf',
            },
            {
                contents: '@videoFileIntRmv',
                fileName: 'videoFileInt.rmv',
            },
        ], { force: true });

        const expectedData = {
            ExpAvf: { '': '', Bv: '132', Bvs: '3.762', 状态: '新标识', 用时: '35.090', 级别: '高级', 结束时间: '2023-10-05 21:25:57' },
            CusAvf: { '': '', Bv: '357', Bvs: '0.415', 状态: '暂不支持自定义级别', 用时: '860.360', 级别: '自定义', 结束时间: '2022-05-22 23:30:49' },
            IntRmv: { '': '', Bv: '32', Bvs: '3.379', 状态: '新标识', 用时: '9.469', 级别: '中级', 结束时间: '2015-10-31 15:53:35' },
        };

        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData.length).to.equal(3);
            expect(tableData[0]).to.deep.equal(expectedData.ExpAvf);
            expect(tableData[1]).to.deep.equal(expectedData.CusAvf);
            expect(tableData[2]).to.deep.equal(expectedData.IntRmv);
        });

        cy.get('table:visible').find('.el-checkbox__input').first().click(); // 全选
        cy.get('button').contains('上传').click();
        cy.get('.el-loading-spinner').should('exist');
        cy.get('.el-loading-spinner').should('not.exist');

        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData.length).to.equal(1);
            expect(tableData[0]).to.deep.equal(expectedData.CusAvf);
        });
    });
});
