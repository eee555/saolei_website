import { VideoAbstract, VideoAbstractInfo } from '@/utils/videoabstract';

interface userProfileInfo {
    id: number;
    username: string;
    realname: string;
    is_banned: boolean;
    is_staff: boolean;
    country: string;
    identifiers: string[];
    videos: VideoAbstractInfo[];
}

export class UserProfile {
    public id: number;
    public username: string;
    public realname: string;
    public is_banned: boolean;
    public is_staff: boolean;
    public country: string;
    public accountlink: any[];
    public identifiers: string[];
    public videos: VideoAbstract[];

    constructor(info?: userProfileInfo) {
        if (info) {
            this.id = info.id;
            this.username = info.username;
            this.realname = info.realname;
            this.is_banned = info.is_banned;
            this.is_staff = info.is_staff;
            this.country = info.country;
            this.accountlink = [];
            this.identifiers = info.identifiers.slice();
            this.videos = info.videos.map((video) => new VideoAbstract(video));
        } else {
            this.id = 0;
            this.username = '';
            this.realname = '';
            this.is_banned = false;
            this.is_staff = false;
            this.country = '';
            this.accountlink = [];
            this.identifiers = [];
            this.videos = [];
        }
    }
}
