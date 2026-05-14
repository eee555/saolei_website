import { GetUserInfoResponse } from './common/structInterface';
import { VideoAbstract } from './videoabstract';

export class UserProfile {
    constructor(
        public id: number = 0,
        public username: string = '',
        public realname: string = '匿名',
        public firstname: string = '',
        public lastname: string = '',
        public is_banned: boolean = false,
        public is_staff: boolean = false,
        public country: string = '',
        public signature: string = '',
        public last_change_avatar: Date = new Date(),
        public last_change_signature: Date = new Date(),
        public left_avatar_n: number = 0,
        public left_signature_n: number = 0,
        public accountlink: any[] = [],
        public identifiers: string[] = [],
        public videos: VideoAbstract[] = [],
    ) {}

    static from(info: GetUserInfoResponse): UserProfile {
        return new UserProfile(
            info.id,
            info.username,
            info.realname,
            info.firstname,
            info.lastname,
            info.is_banned,
            info.is_staff,
            info.country,
            info.signature,
            new Date(info.last_change_avatar),
            new Date(info.last_change_signature),
            info.left_avatar_n,
            info.left_signature_n,
        );
    }

    public newAvatarBudget(newDate: Date) {
        return this.left_avatar_n + newDate.getUTCFullYear() - this.last_change_avatar.getUTCFullYear();
    }

    get nextAvatarAvailable() {
        if (this.left_avatar_n > 0) return this.last_change_avatar;
        const year = this.last_change_avatar.getUTCFullYear();
        const targetTimestamp = Date.UTC(year + 1, 0, 1, 0, 0, 0);
        return new Date(targetTimestamp);
    }
}
