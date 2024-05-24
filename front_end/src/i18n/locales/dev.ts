import { LocaleConfig } from '@/i18n/config'

export const dev: LocaleConfig = {
    local: 'dev',
    name: 'name',
    common: {
        time: 'common.time'
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
    login: {
        title: 'login.title',
        username: 'login.username',
        password: 'login.password',
        captcha: 'login.captcha',
        forgetPassword: 'login.forgetPassword',
        keepMeLoggedIn: 'login.keepMeLoggedIn',
        confirm: 'login.confirm'
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
    example: {
        placeholder: 'example.placeholder: {0}',
    },
}