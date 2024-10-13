const saoleiProfile = (id: string | number) => {
    return "http://saolei.wang/Player/Index.asp?Id=" + id;
}
const msgamesProfile = (id: string | number) => {
    return "https://minesweepergame.com/profile.php?pid=" + id;
}
const womProfile = (id: string | number) => {
    return "https://minesweeper.online/player/" + id;
}

export declare type Platform = 'a' | 'c' | 'w';
export const platformlist:{[key in Platform]: any;} = {
    a: { name: 'Authoritative Minesweeper', url: 'https://minesweepergame.com/', profile: msgamesProfile },
    c: { name: '扫雷网', url: 'http://saolei.wang/', profile: saoleiProfile },
    w: { name: 'Minesweeper.Online', url: 'https://minesweeper.online/', profile: womProfile },
};

