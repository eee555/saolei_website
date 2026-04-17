import Footer from './Footer.vue';

import i18n from '@/i18n';

const mountOptions = {
    global: {
        plugins: [i18n],
    },
};

describe('<Footer />', () => {
    it('renders all sections', () => {
        cy.mount(Footer, mountOptions);

        // 测试关于我们部分
        cy.contains('About');

        // 测试联系我们部分
        cy.contains('Contact');

        // 测试友链部分
        cy.contains('Links');
    });

    it('renders contact links', () => {
        cy.mount(Footer, mountOptions);

        // 测试GitHub链接
        cy.contains('GitHub').should('have.attr', 'href', 'https://github.com/eee555/saolei_website').and('have.attr', 'target', '_blank');

        // 测试Gitee链接
        cy.contains('Gitee').should('have.attr', 'href', 'https://gitee.com/ee55/saolei_website').and('have.attr', 'target', '_blank');

        // 测试Discord链接
        cy.contains('Discord').should('have.attr', 'href', 'https://discord.gg/ks8ngPX5bT').and('have.attr', 'target', '_blank');

        // 测试QQ链接
        cy.contains('QQ').should('have.attr', 'href', 'https://qm.qq.com/q/hNShGUQkJG').and('have.attr', 'target', '_blank');
    });

    it('renders friendly links', () => {
        cy.mount(Footer, mountOptions);

        // 测试扫雷网链接
        cy.contains('扫雷网 saolei.wang').should('have.attr', 'href', 'http://saolei.wang').and('have.attr', 'target', '_blank');

        // 测试Authoritative Minesweeper链接
        cy.contains('Authoritative Minesweeper').should('have.attr', 'href', 'https://minesweepergame.com').and('have.attr', 'target', '_blank');

        // 测试Minesweeper.Online链接
        cy.contains('Minesweeper.Online').should('have.attr', 'href', 'https://minesweeper.online').and('have.attr', 'target', '_blank');

        // 测试扫雷联萌链接
        cy.contains('扫雷联萌 League of Minesweeper').should('have.attr', 'href', 'http://tapsss.com').and('have.attr', 'target', '_blank');

        // 测试Scoreganizer链接
        cy.contains('Scoreganizer').should('have.attr', 'href', 'https://scoreganizer.net').and('have.attr', 'target', '_blank');
    });

    it('renders copyright section', () => {
        cy.mount(Footer, mountOptions);

        // 测试版权文本
        cy.contains('Copyright @ 2023');
        cy.contains('版权所有');

        // 测试开源扫雷网链接
        cy.contains('开源扫雷网 openms.top').should('have.attr', 'href', 'http://openms.top');

        // 测试ICP备案链接
        cy.contains('苏ICP备2023056839号-1').should('have.attr', 'href', 'https://beian.miit.gov.cn/');

        // 测试公安备案链接
        cy.contains('苏公网安备32020602001691').should('have.attr', 'href', 'https://beian.mps.gov.cn/#/query/webSearch?code=32020602001691').and('have.attr', 'target', '_blank');
    });

    it('opens and closes team dialog', () => {
        cy.viewport(500, 1000);
        cy.mount(Footer, mountOptions);

        // 点击团队链接
        cy.contains('Team').click();

        // 验证对话框已打开
        cy.get('.el-dialog').should('be.visible');

        // 点击对话框外部关闭
        cy.get('body').click(0, 0);

        // 验证对话框已关闭
        cy.get('.el-dialog').should('not.be.visible');
    });

    it('opens and closes downloads dialog', () => {
        cy.viewport(500, 1000);
        cy.mount(Footer, mountOptions);

        // 点击软件下载链接
        cy.contains('Software Downloads').click();

        // 验证对话框已打开
        cy.get('.el-dialog').should('be.visible');

        // 点击对话框外部关闭
        cy.get('body').click(0, 0);

        // 验证对话框已关闭
        cy.get('.el-dialog').should('not.be.visible');
    });
});
