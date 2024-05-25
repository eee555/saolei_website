import { LocaleConfig } from '@/i18n/config'

export const dev: LocaleConfig = {
    local: 'dev',
    name: 'name',
    common: {
        time: 'common.time'
    },
    forgetPassword: {
        title: 'forgetPassword.title',
        email: 'forgetPassword.email',
        captcha: 'forgetPassword.captcha',
        getEmailCode: 'forgetPassword.getEmailCode',
        emailCode: 'forgetPassword.emailCode',
        password: 'forgetPassword.password',
        confirmPassword: 'forgetPassword.confirmPassword',
        confirm: 'forgetPassword.confirm'
    },
    login: {
        title: 'login.title',
        username: 'login.username',
        password: 'login.password',
        captcha: 'login.captcha',
        forgetPassword: 'login.forgetPassword',
        keepMeLoggedIn: 'login.keepMeLoggedIn',
        confirm: 'login.confirm'
    },
    menu: {
        ranking: 'menu.ranking',
        video: 'menu.video',
        world: 'menu.world',
        guide: 'menu.guide',
        score: 'menu.score',
        profile: 'menu.profile',
        welcome: `menu.welcome{'{'}0{'}'}`,
        login: 'menu.login',
        logout: 'menu.logout',
        register: 'menu.register',
        downloads: 'menu.downloads',
        links: 'menu.links',
        team: 'menu.team'
    },
    profile: {
        changeAvatar: 'profile.changeAvatar',
        realname: 'profile.realname',
        realnameInput: 'profile.realnameInput',
        signature: 'profile.signature',
        signatureInput: 'profile.signatureInput',
        change: 'profile.change',
        confirmChange: 'profile.confirmChange',
        cancelChange: 'profile.cancelChange',
        designator: 'profile.designator'
    },
    register: {
        title: 'register.title',
        username: 'register.username',
        email: 'register.email',
        captcha: 'register.captcha',
        getEmailCode: 'register.getEmailCode',
        emailCode: 'register.emailCode',
        password: 'register.password',
        confirmPassword: 'register.confirmPassword',
        agreeTo: 'register.agreeTo',
        termsAndConditions: 'register.termsAndConditions',
        confirm: 'register.confirm'
    },
    example: {
        placeholder: 'example.placeholder: {0}',
    },
}