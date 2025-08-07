// 注册、登录、找回密码
import 'cypress-if';

function expectNotLoggedIn() {
    cy.contains('登录').should('be.visible');
    cy.contains('注册').should('be.visible');
    cy.contains('退出').if().should('not.be.visible');
}

function expectLoggedIn() {
    cy.contains('退出').should('be.visible');
    cy.contains('登录').if().should('not.be.visible');
    cy.contains('注册').if().should('not.be.visible');
}

describe('User Authentication', () => {
    it('Popup Functions', () => {
        // 初始状态
        cy.visit('/settings');
        expectNotLoggedIn();
        cy.contains('用户注册').should('not.exist');
        cy.contains('用户登录').should('not.exist');

        // 打开并关闭注册界面
        cy.contains('注册').click();
        cy.contains('用户注册').should('be.visible');
        cy.contains('用户注册').next().click();
        cy.contains('用户注册').should('not.be.visible');

        // 打开并关闭登录界面
        cy.contains('登录').click();
        cy.contains('用户登录').should('be.visible');
        cy.contains('用户登录').next().click();
        cy.contains('用户登录').should('not.be.visible');
    });

    it('Register', () => {
        // 打开注册界面
        cy.visit('/settings');
        cy.contains('注册').click();

        // 填写注册信息
        cy.contains('用户名').next().find('input').type('testUser');
        cy.contains('邮箱').next().find('input').type('testUser@example.com');
        cy.contains('图形验证码').next().find('input').type('test');
        cy.contains('发送').click();
        cy.contains('邮箱验证码').next().find('input').type('abcdef');
        cy.contains('密码').next().find('input').type('testPassword');
        cy.contains('确认密码').next().find('input').type('testPassword');
        cy.contains('已阅读并同意').find('input').parent().click();

        // 完成注册
        cy.contains('用户注册').parent().parent().find('button').contains('注册').click();
        cy.contains('注册成功');
        cy.contains('用户注册').should('not.be.visible');

        // 退出登录
        expectLoggedIn();
        cy.closeElNotifications();
        cy.contains('退出').click();
        expectNotLoggedIn();
    });

    it('Login & Logout', () => {
        // 打开登录界面
        cy.visit('/settings');
        expectNotLoggedIn();
        cy.contains('登录').click();

        // 填写登录信息
        cy.contains('用户名').next().find('input').type('testUser');
        cy.contains('密码').next().find('input').type('testPassword');
        cy.contains('验证码').next().find('input').type('test');

        // 完成登录
        cy.contains('用户登录').parent().parent().find('button').contains('登录').click();
        cy.contains('用户登录').should('not.be.visible');
        expectLoggedIn();

        // 刷新页面
        cy.reload();
        expectNotLoggedIn();
    });

    it('Remember Me', () => {
        cy.visit('/settings');
        expectNotLoggedIn();

        // 登录
        cy.contains('登录').click();
        cy.contains('用户名').next().find('input').type('testUser');
        cy.contains('密码').next().find('input').type('testPassword');
        cy.contains('验证码').next().find('input').type('test');
        cy.contains('记住我').click();
        cy.contains('用户登录').parent().parent().find('button').contains('登录').click();
        cy.contains('用户登录').should('not.be.visible');
        expectLoggedIn();

        // 刷新
        cy.reload();
        expectLoggedIn();
        cy.reload();
        expectLoggedIn();
        cy.contains('退出').click();
        cy.reload();
        expectNotLoggedIn();
    });

    it('Forget Password', () => {
        cy.visit('/settings');
        expectNotLoggedIn();

        // 尝试用错误密码登录
        cy.contains('登录').click();
        cy.contains('用户名').next().find('input').type('testUser');
        cy.contains('密码').next().find('input').type('newPassword');
        cy.contains('验证码').next().find('input').type('test');
        cy.contains('用户登录').parent().parent().find('button').contains('登录').click();
        cy.contains('用户名或密码不正确');
        expectNotLoggedIn();

        // 打开找回密码界面
        cy.contains('忘记密码').click();
        cy.contains('修改密码').should('be.visible');
        cy.contains('用户登录').should('not.be.visible');

        // 填写找回密码信息
        cy.contains('邮箱').next().find('input').type('testUser@example.com');
        cy.contains('图形验证码').next().find('input').type('test');
        cy.contains('发送').click();
        cy.contains('邮箱验证码').next().find('input').type('abcdef');
        cy.get('label').filter(':visible').contains(/^密码$/).next().find('input').type('newPassword');
        cy.contains('确认密码').next().find('input').type('newPassword');

        // 完成找回密码
        cy.contains('修改密码').parent().parent().find('button').contains('确认').should('be.enabled');
        cy.contains('修改密码').parent().parent().find('button').contains('确认').click();
        cy.contains('修改密码').should('not.be.visible');
        cy.closeElNotifications();
        expectLoggedIn();

        cy.reload();
        expectNotLoggedIn();
    });
});
