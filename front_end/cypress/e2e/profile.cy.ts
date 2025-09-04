// 个人主页
import 'cypress-if';
import 'cypress-get-table';
import { binaryStringToUint8Array } from '../support/stupidCypress';

const UPLOAD_BUTTON = '.pi-upload';

describe('Personal Profile', () => {
    before(() => {
        // 初始化数据库
        cy.flushDatabase();

        // 准备录像文件
        cy.request({
            url: 'https://github.com/putianyi889/replays/raw/refs/heads/master/EXP/sub40/Exp_FL_35.09_3BV=132_3BVs=3.76_Pu%20Tian%20Yi(Hu%20Bei).avf',
            encoding: 'binary',
        }).then((resp) => {
            cy.wrap(binaryStringToUint8Array(resp.body)).as('videoFileExp'); // alias it for later use in same test
        });
        cy.request({
            url: 'https://minesweepergame.com/member/file/4376/4376-Custom-FL-30x24-860.360-357-226m-20220522.avf',
            encoding: 'binary',
        }).then((resp) => {
            cy.wrap(binaryStringToUint8Array(resp.body)).as('videoFileCus'); // alias it for later use in same test
        });

        // 注册并登录用户
        cy.register('testUser', 'test@email.com', 'testPassword');
        cy.login('testUser', 'testPassword');
    });

    it.skip('Guest view', () => {
        cy.visit('/#/player/1');
        cy.contains('个人信息');
        cy.contains('个人纪录');
        cy.contains('全部录像');
        cy.contains('上传录像').should('not.exist');
    });

    it.skip('Cannot upload videos without real name', () => {
        cy.login('testUser', 'testPassword');
        cy.visit('/#/player/1');
        cy.contains('上传录像').click();
        cy.contains('请修改为实名');
    });

    it.skip('Change real name', () => {
        cy.login('testUser', 'testPassword');
        cy.visit('/#/player/1');
        cy.contains('修改简介').click();
        cy.contains('修改简介').if().should('not.be.visible');

        cy.contains('姓名').next().find('input').clear();
        cy.contains('姓名').next().find('input').type('testName');
        cy.contains('确认').click();

        cy.contains('修改简介').if().should('be.visible');
    });

    it('Parse video', () => {
        cy.login('testUser', 'testPassword');
        cy.visit('/#/player/1');
        cy.contains('上传录像').click();

        cy.get('input[type=file]').selectFile([
            {
                contents: '@videoFileExp',
                fileName: 'videoFileExp.avf',
            },
            {
                contents: '@videoFileCus',
                fileName: 'videoFileCus.avf',
            }, // ms-toollib 暂时有bug，无法解析自定义级别录像
        ], { force: true });

        cy.contains('新标识');
        cy.get('table:visible').getTable().should((tableData) => {
            expect(tableData[0].Bv).to.equal('132');
            expect(tableData[0].Bvs).to.equal('3.762');
            expect(tableData[0].状态).to.equal('新标识');
            expect(tableData[0].用时).to.equal('35.090');
            expect(tableData[0].级别).to.equal('高级');
            expect(tableData[0].结束时间).to.equal('2023-10-06 05:25:57');
        });
        cy.get('table:visible').find('tbody').find('i').find(UPLOAD_BUTTON);
    });
});
