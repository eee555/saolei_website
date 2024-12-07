export default {
    local: 'en',
    name: 'English',
    common: {
        action: {
            addIdentifier: 'add identifier',
            getSoftware: 'fetch video data',
            getUserProfile: 'fetch user data',
            getVideoModel: 'fetch video data',
            setUserProfile: 'modify user data',
            setVideoModel: 'modify video data',
            uploadFile: 'upload file',
            videoQuery: 'fetch video data',
        },
        button: {
            cancel: 'Cancel',
            confirm: 'Confirm',
            send: 'Send',
        },
        filter: 'Filter',
        hide: 'Hide',
        level: {
            b: 'Beginner',
            i: 'Intermediate',
            e: 'Expert',
            sum: 'Sum',
        },
        mode: {
            std: 'Standard',
            nf: 'No Flag',
            ng: 'No Guessing',
            dg: 'Recursive Chord',
            sng: 'Strict No Guessing',
        },
        msg: {
            actionFail: 'Failed to {0}',
            actionSuccess: 'Succeed to {0}',
            agreeTAC: 'Please agree to Terms and Conditions!',
            connectionFail: 'Connection Fails!',
            contactDeveloper: 'Please contact the developers.',
            fileTooLarge: 'Maximum file size is {0}',
            logoutFail: 'Failed to log out!',
            logoutSuccess: 'Log out success!',
            realNameRequired: 'Real name required',
            unknownError: 'An unknown error has occurred.',
        },
        prop: {
            action: 'Action',
            identifier: 'Identifier',
            fileName: 'File name',
            is: 'Island',
            level: 'Level',
            mastery: 'Mastery',
            op: 'Opening',
            realName: 'Real Name',
            sex: 'Sex',
            state: 'State', // video attribute
            status: 'Status',
            time: 'Time',
            timems: 'Time',
            update_time: 'Update Time',
            upload_time: 'Upload Time',
            winstreak: 'Win Streak',
        },
        response: {
            OK: '',
            BadRequest: 'Unrecognised request',
            Forbidden: 'Permission denied',
            InternalServerError: 'Internal server error',
            NotFound: 'Data not found',
            PayloadTooLarge: 'Payload too large',
            TooManyRequests: 'Too many requests',
            UnsupportedMediaType: 'Unsupported file type',
        },
        show: 'Show',
        software: {
            resource_download: 'Downloads',
            software_download: 'Software',
            download_link: 'Resource',
            metasweeper: 'MetaSweeper',
            metasweeper_int: '',
            metasweeper_int2: '',
            arbiter_int: '',
        },
        state: {
            a: 'Pending',
            b: 'Frozen',
            c: 'Valid',
            d: 'Identifier Mismatch',
        },
        toDo: 'TODO',
    },
    accountlink: {
        title: 'Account Links',
        addLink: 'Link New Account',
        deleteLinkMessage: 'Are you sure to unlink this account?',
        guideMsgames1: 'Find yourself on the ',
        guideMsgames2: ' ranking:',
        guideMsgames3: 'Click the link next to your name (see image above) to get to your profile (see image below). The number at the end of the url is your ID.',
        guideSaolei1: 'Go to your profile page on ',
        guideSaolei2: '. The positions of the ID are shown below.',
        guideTitle: 'How to locate the ID',
        guideWom1: 'Go to your profile page on ',
        guideWom2: '. The number at the end of the url is your ID.',
        msgamesJoined: 'Joined',
        msgamesLocalName: 'Local Name',
        msgamesName: 'Name',
        platform: 'Platform',
        saoleiName: 'Name',
        saoleiTotalViews: 'Total Views',
        saoleiVideoCount: 'Video Count',
        unverified: 'Pending. Please contact the moderator.',
        unverifiedText: 'This account has not been verified. Please contact a moderator.',
        updateError: {
            cooldown: 'Cannot update twice in 12 hours',
            empty: 'Empty data',
            indexerror: 'Failed to extract data',
            timeout: 'Cannot connect to the platform',
            title: 'Update failed',
            unknown: 'Unknown error',
        },
        verified: 'Verified',
        womArenaPoint: 'Arena',
        womExperience: 'Experience',
        womLastSeason: 'Last Season',
        womMaxDifficulty: 'Max Difficulty',
        womResource: 'Resources',
        womTrophy: 'Trophies',
        womWin: 'Wins',
    },
    footer: {
        contact: 'Contact',
        donate: 'Donate',
        team: 'Team',
        links: 'Links',
        about: 'About',
    },
    form: {
        captcha: 'captcha',
        confirmPassword: 'confirm password',
        email: 'email',
        emailCode: 'Email code',
        imageCaptcha: 'Image captcha',
        password: 'Password',
        username: 'Username',
    },
    guide: {
        announcement: 'Announcements',
        other: 'Others',
        skill: 'Skills',
        tutorial: 'Tutorials',
    },
    home: {
        news: 'News',
        latestScore: 'Latest',
        reviewQueue: 'Pending',
    },
    identifierManager: {
        title: 'Minesweeper Identifiers',
        addIdentifierSuccess: 'Identifier Added',
        conflict: 'Identifier Conflict',
        delIdentifierSuccess: 'Identifier Deleted',
        processedNVideos: '{0} videos have been processed',
        ownedBy: 'The identifier is owned by user#{0}',
        notFound: 'You do not have any video of the identifier',
    },
    login: {
        agreeTAC1: 'Agree to',
        agreeTAC2: 'Terms & Conditions',
        forgetPassword: 'Forget password?',
        keepMeLoggedIn: 'Keep me logged in',
        loginConfirm: 'Log in',
        loginTitle: 'Login',
        registerConfirm: 'Register',
        registerTitle: 'Register',
        retrieveConfirm: 'Update password',
        retrieveTitle: 'Account Recovery',
    },
    menu: {
        ranking: 'Ranking',
        video: 'Videos',
        world: 'Statistics',
        guide: 'Guides',
        score: 'Scores',
        profile: 'Profile',
        welcome: `Welcome, {0}!`,
        login: 'Login',
        logout: 'Logout',
        register: 'Register',
        setting: 'Settings',
    },
    msg: {
        actionFail: 'Action failed',
        actionSuccess: 'Action success',
        captchaFail: 'Invalid captcha. Please input again',
        captchaRefresh: 'Please input again',
        captchaRequired: 'Captcha required',
        confirmPasswordMismatch: 'Mismatches password',
        connectionFail: 'Connection failed. Please try again',
        copyToClipboardFail: 'Failed to copy.',
        copyToClipboardSuccess: 'Text copied.',
        emailCodeInvalid: 'Email code is invalid or expired',
        emailCodeRequired: 'Email code required',
        emailCollision: 'Email already exists',
        emailInvalid: 'Invalid email address',
        emailNoCollision: 'Email does not exist',
        emailRequired: 'Email required',
        emailSendFailMsg: 'Please re-enter captcha. If this happens again, please contact the developers.',
        emailSendFailTitle: 'Failed to send email',
        emailSendSuccessMsg: 'Please check your email inbox',
        emailSendSuccessTitle: 'Email is sent',
        fail: 'Failed: ',
        illegalCharacter: 'Illegal character',
        passwordChanged: 'Password updated',
        passwordMinimum: 'Password requires at least 6 characters',
        passwordRequired: 'Password required',
        pleaseWait: 'Please wait',
        pleaseSeeEmail: 'Please check your email',
        registerSuccess: 'Successfully registered!',
        success: 'Success: ',
        unknownError: 'An unexpected error occurred. Please contact the developers. {0}',
        usernameCollision: 'Username already exists',
        usernameInvalid: 'Username must contain visible characters',
        usernamePasswordInvalid: 'Invalid username or password',
        usernameRequired: 'Username required',
    },
    news: {
        breakRecordTo: ' breaks their {mode} {level} {stat} record with ',
    },
    profile: {
        changeAvatar: 'Click the image to change avatar',
        realname: 'Name: ',
        realnameInput: 'Input your real name here',
        signature: 'Bio: ',
        signatureInput: 'Input your bio here',
        change: 'Edit profile',
        confirmChange: 'Confirm',
        cancelChange: 'Cancel',
        identifier: 'My identifiers: ',
        msg: {
            avatarChange: 'Avatar change complete! {0} times left',
            avatarFormat: 'Avatar file has to be in JPG or PNG format!',
            avatarFilesize: 'Maximum file size is 50MB!',
            realnameChange: 'Real name change complete! {0} times left',
            signatureChange: 'Signature change complete! {0} times left',
        },
        profile: {
            title: 'Profile',
        },
        records: {
            title: 'Personal Records',
            modeRecord: ' mode record: '
        },
        videos: 'All videos',
        exportJSON: 'Export as JSON',
        exportJSONTooltip: 'Raw data fetched from the server.',
        exportArbiterCSV: 'Export as CSV',
        exportArbiterCSVTooltip: 'Compatible with <span style="font-family: \'Courier New\', Courier, monospace;">stats_csv.csv</span> generated by Minesweeper Arbiter.<br/> Not supporting Leff, Reff, Deff, GZiNi and HZiNi at present.',
        upload: {
            title: 'Video Upload',
            dragOrClick: `Drag files here or <em>click here to select</em>`,
            uploadAll: 'Upload All ({0})',
            cancelAll: 'Clear All',
            constraintNote: '*File size maximum is 5MB.',
            error: {
                collision: 'Video already exist',
                custom: 'Custom level is currently not supported',
                identifier: 'New identifier',
                fail: 'Fail',
                fileext: 'Invalid file extension',
                filename: 'File name exceeds 100 bytes',
                filesize: 'File size exceeds 5MB',
                mode: 'Unsupported game mode',
                needApprove: 'Need manual approval',
                pass: 'Pass',
                process: 'Uploading',
                upload: 'Upload fail',
            }
        }
    },
    setting: {
        appearance: 'Appearance',
        colorscheme: {
            auto: 'auto',
            dark: 'dark',
            light: 'light',
            title: 'Color scheme',
        },
        languageSwitch: 'Language Switch',
        menuFontSize: 'Menu Font Size',
        menuHeight: 'Menu Height',
        menuLayout: 'Menu Layout',
        menuLayoutAbstract: 'Abstract',
        menuLayoutDefault: 'Default',
        newUserGuide: 'Get Help',
        newUserGuideTooltip: 'Get help by hovering over components',
        notificationDuration: 'Notification Duration',
        notificationDurationTooltip: 'Duration before close. <br />It will not automatically close if set 0.',
    },
    team: {
        title: 'Team',
        owner: 'Owner',
        moderator: 'Moderators',
        software: 'Developers',
        localization: 'Localization',
        zhCn: 'Simplified Chinese',
        en: 'English',
        de: 'German',
        pl: 'Polish',
        designer: 'UI designers',
        acknowledgement: 'Acknowledgement',
    },
}