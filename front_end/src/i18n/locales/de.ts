
import { LocaleConfig } from '@/i18n/config'

export const dev: LocaleConfig = {
    local: 'dev',
    name: 'name',
    common: {
        time: 'common.time'
    },
    forgetPassword: {
        title: 'Titel',
        email: 'E-Mail',
        captcha: 'Captcha',
        getEmailCode: 'E-Mail Code anfordern',
        emailCode: 'E-Mail Code',
        password: 'Passwort',
        confirmPassword: 'Passwort bestätigen',
        confirm: 'bestätigen'
    },
    login: {
        title: 'Titel',
        username: 'Benutzername',
        password: 'Passwort',
        captcha: 'Captcha',
        forgetPassword: 'Passwort vergessen?',
        keepMeLoggedIn: 'eingeloggt bleiben',
        confirm: 'Login'
    },
    menu: {
        ranking: 'Ranking',
        video: 'Video',
        world: 'Welt',
        guide: 'Hilfe',
        score: 'Ergebnisse',
        profile: 'Profil',
        welcome: `Willkommen{'{'}0{'}'}`,
        login: 'Login',
        logout: 'Abmeldem',
        register: 'Registrieren',
        downloads: 'Downloads',
        links: 'Links',
        team: 'Team'
    },
    profile: {
        changeAvatar: 'Profilbild ändern',
        realname: 'Name',
        realnameInput: 'profile.realnameInput',
        signature: 'profile.signature',
        signatureInput: 'profile.signatureInput',
        change: 'profile.change',
        confirmChange: 'Änderungen bestätigen',
        cancelChange: 'abbrechen',
        designator: 'profile.designator'
    },
    register: {
        title: 'Titel',
        username: 'Benutzername',
        email: 'E-mail',
        captcha: 'Captcha',
        getEmailCode: 'E-mail Code erhalten',
        emailCode: 'E-Mail Code',
        password: 'Passwort',
        confirmPassword: 'Passwort',
        agreeTo: 'Zustimmen',
        termsAndConditions: 'Nutzungsbedingungen',
        confirm: 'bestätigen'
    },
    example: {
        placeholder: 'example.placeholder: {0}',
    },
}
