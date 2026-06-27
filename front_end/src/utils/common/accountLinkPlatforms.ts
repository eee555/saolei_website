const saoleiProfile = (id: string | number): string => 'http://saolei.wang/Player/Index.asp?Id=' + id;
const msgamesProfile = (id: string | number): string => 'https://minesweepergame.com/profile.php?pid=' + id;
const womProfile = (id: string | number): string => 'https://minesweeper.online/player/' + id;
const qqProfile = (id: string | number): string => 'https://user.qzone.qq.com/' + id;
const bilibiliProfile = (id: string | number): string => 'https://space.bilibili.com/' + id;

export declare type Platform = 'B' | 'a' | 'c' | 'q' | 'w';
interface PlatformProfile {
    name: string;
    url: string;
    profile: (id: string | number) => string;
}
export const platformlist: Record<Platform, PlatformProfile> = {
    B: { name: 'Bilibili', url: 'https://www.bilibili.com/', profile: bilibiliProfile },
    a: { name: 'Authoritative Minesweeper', url: 'https://minesweepergame.com/', profile: msgamesProfile },
    c: { name: '扫雷网', url: 'http://saolei.wang/', profile: saoleiProfile },
    q: { name: '腾讯QQ', url: 'https://im.qq.com/index/', profile: qqProfile },
    w: { name: 'Minesweeper.Online', url: 'https://minesweeper.online/', profile: womProfile },
};

