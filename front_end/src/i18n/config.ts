import type { VueMessageType } from 'vue-i18n';
import { LocaleMessage } from '@intlify/core-base';

/**
 * 配置语法：https://vue-i18n.intlify.dev/guide/essentials/syntax.html
 */
export type LocaleConfig = LocaleMessage<VueMessageType> & {
    // 当前语言唯一标识
    local: string;
    // 嵌套配置示例 TODO 删除嵌套配置示例
    name: string;
    common: {
        action: {
            addIdentifier: string;
            getSoftware: string;
            getUserProfile: string;
            getVideoModel: string;
            setUserProfile: string;
            setVideoModel: string;
            uploadFile: string;
            videoQuery: string;
        };
        hide: string;
        level: {
            b: string;
            i: string;
            e: string;
            sum: string;
        };
        mode: {
            std: string;
            nf: string;
            ng: string;
            dg: string;
            sng: string;
        };
        msg: {
            actionFail: string;
            actionSuccess: string;
            agreeTAC: string;
            confirmPasswordFail: string;
            connectionFail: string;
            contactDeveloper: string;
            emailCodeSent: string;
            emptyEmail: string;
            emptyEmailCode: string;
            emptyPassword: string;
            emptyUsername: string;
            fileTooLarge: string;
            invalidEmail: string;
            invalidEmailCode: string;
            invalidPassword: string;
            invalidUsername: string;
            logoutFail: string;
            logoutSuccess: string;
            realNameRequired: string;
            unknownError: string;
        };
        prop: {
            action: string;
            identifier: string;
            fileName: string;
            is: string;
            op: string;
            level: string;
            realName: string;
            sex: string;
            status: string;
            time: string;
            timems: string;
            upload_time: string;
        };
        response: {
            OK: '';
            BadRequest: string;
            Forbidden: string;
            InternalServerError: string;
            NotFound: string;
            PayloadTooLarge: string;
            TooManyRequests: string;
            UnsupportedMediaType: string;
        };
        show: string;
        software: {
            resource_download: string;
            software_download: string;
            download_link: string;
            metasweeper: string;
            metasweeper_int: string; // introduction
            arbiter_int: string;
        };
        toDo: string;
    };
    forgetPassword: {
        title: string;
        email: string;
        captcha: string;
        getEmailCode: string;
        emailCode: string;
        password: string;
        confirmPassword: string;
        confirm: string;
        success: string;
    };
    login: {
        title: string;
        username: string;
        password: string;
        captcha: string;
        forgetPassword: string;
        keepMeLoggedIn: string;
        confirm: string;
    };
    menu: {
        ranking: string;
        video: string;
        world: string;
        guide: string;
        score: string;
        profile: string;
        welcome: string;
        login: string;
        logout: string;
        register: string;
        setting: string;
    };
    profile: {
        changeAvatar: string;
        realname: string;
        realnameInput: string;
        signature: string;
        signatureInput: string;
        change: string;
        confirmChange: string;
        cancelChange: string;
        identifier: string;
        msg: {
            avatarChange: string;
            avatarFormat: string;
            avatarFilesize: string;
            realnameChange: string;
            signatureChange: string;
        };
        records: {
            title: string;
            modeRecord: string;
        };
        videos: string;
        upload: {
            title: string;
            dragOrClick: string;
            uploadAll: string;
            cancelAll: string;
            constraintNote: string;
            error: {
                collision: string;
                custom: string;
                identifier: string;
                fail: string;
                fileext: string;
                filename: string;
                filesize: string;
                mode: string;
                needApprove: string;
                pass: string;
                process: string;
                upload: string;
            };
        };
    };
    register: {
        title: string;
        username: string;
        email: string;
        captcha: string;
        getEmailCode: string;
        emailCode: string;
        password: string;
        confirmPassword: string;
        agreeTo: string;
        termsAndConditions: string;
        confirm: string;
    };
    setting: {
        appearance: string;
        colorscheme: {
            auto: string;
            dark: string;
            light: string;
            title: string;
        };
        languageSwitch: string;
        menuFontSize: string;
        menuHeight: string;
        menuLayout: string;
        menuLayoutAbstract: string;
        menuLayoutDefault: string;
    };
    team: {
        title: string;
        owner: string;
        moderator: string;
        software: string;
        localization: string;
        zhCn: string;
        en: string;
        de: string;
        pl: string;
        designer: string;
        acknowledgement: string;
    };
};
