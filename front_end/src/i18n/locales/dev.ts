import { LocaleConfig } from '@/i18n/config'

export const dev: LocaleConfig = {
    local: 'dev',
    name: 'name',
    common: {
        level: {
            b: 'common.level.b',
            i: 'common.level.i',
            e: 'common.level.e',
        },
        mode: {
            standard: 'common.mode.standard',
            noFlag: 'common.mode.noFlag',
            noGuess: 'common.mode.noGuess',
            recursive: 'common.mode.recursive'
        },
        prop: {
            action: 'common.prop.action',
            designator: 'common.prop.designator',
            fileName: 'common.prop.fileName',
            level: 'common.prop.level',
            status: 'common.prop.status',
            time: 'common.prop.time',
        }
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
        designator: 'profile.designator',
        records: {
            title: 'profile.records.title',
            modeRecord: 'profile.records.modeRecord'
        },
        videos: 'profile.videos',
        upload: {
            title: 'profile.upload.title',
            dragOrClick: 'profile.upload.dragOrClick',
            uploadAll: 'profile.upload.uploadAll',
            cancelAll: 'profile.upload.cancelAll',
            constraintNote: 'profile.upload.constraintNote',
            error: {
                collision: 'profile.upload.error.collision',
                custom: 'profile.upload.error.custom',
                designator: 'profile.upload.error.designator',
                fail: 'profile.upload.error.fail',
                fileext: 'profile.upload.error.fileext',
                filename: 'profile.upload.error.filename',
                filesize: 'profile.upload.error.filesize',
                pass: 'profile.upload.error.pass',
                process: 'profile.upload.error.process',
                upload: 'profile.upload.error.upload',
            }
        }
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
}