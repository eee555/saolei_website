const saoleiProfile = (id: string | number): string => 'http://saolei.wang/Player/Index.asp?Id=' + id;
const msgamesProfile = (id: string | number): string => 'https://minesweepergame.com/profile.php?pid=' + id;
const womProfile = (id: string | number): string => 'https://minesweeper.online/player/' + id;
const qqProfile = (id: string | number): string => 'https://user.qzone.qq.com/' + id;
const bilibiliProfile = (id: string | number): string => 'https://space.bilibili.com/' + id;

export const AccountLinkPlatform = {
    Bilibili: 'B',
    MSGames: 'a',
    QQ: 'q',
    Saolei: 'c',
    WoM: 'w',
} as const;
export type AccountLinkPlatform = typeof AccountLinkPlatform[keyof typeof AccountLinkPlatform];

interface AccountLinkPlatformProfile {
    name: string;
    url: string;
    profile: (id: string | number) => string;
}

export const platformlist: Record<AccountLinkPlatform, AccountLinkPlatformProfile> = {
    [AccountLinkPlatform.Bilibili]: { name: 'Bilibili', url: 'https://www.bilibili.com/', profile: bilibiliProfile },
    [AccountLinkPlatform.MSGames]: { name: 'Authoritative Minesweeper', url: 'https://minesweepergame.com/', profile: msgamesProfile },
    [AccountLinkPlatform.Saolei]: { name: '扫雷网', url: 'http://saolei.wang/', profile: saoleiProfile },
    [AccountLinkPlatform.QQ]: { name: '腾讯QQ', url: 'https://im.qq.com/index/', profile: qqProfile },
    [AccountLinkPlatform.WoM]: { name: 'Minesweeper.Online', url: 'https://minesweeper.online/', profile: womProfile },
};
