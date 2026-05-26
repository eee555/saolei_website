import { VideoAbstract } from './videoabstract';

export class UserProfile {
    public id: number = 0;
    public username: string = '';
    public realname: string = '匿名';
    public firstname: string = '';
    public lastname: string = '';
    public is_banned: boolean = false;
    public is_staff: boolean = false;
    public country: string = '';
    public signature: string = '';
    public last_change_avatar: Date = new Date();
    public last_change_signature: Date = new Date();
    public left_avatar_n: number = 0;
    public left_signature_n: number = 0;
    public accountlink: any[] = [];
    public identifiers?: string[];
    public videos?: VideoAbstract[];

    constructor(data?: any) {
        if (!data) return;
        this.id = data.id ?? 0;
        this.username = data.username ?? '';

        if (data.realname === '匿名') this.realname = '';
        else this.realname = data.realname ?? '';

        this.firstname = data.firstname ?? '';
        this.lastname = data.lastname ?? '';
        this.is_banned = data.is_banned ?? false;
        this.is_staff = data.is_staff ?? false;
        this.country = data.country ?? '';
        this.signature = data.signature ?? '';

        this.last_change_avatar = data.last_change_avatar ? new Date(data.last_change_avatar) : new Date();
        this.last_change_signature = data.last_change_signature ? new Date(data.last_change_signature) : new Date();

        this.left_avatar_n = data.left_avatar_n ?? 0;
        this.left_signature_n = data.left_signature_n ?? 0;

        this.identifiers = data.identifiers;
        this.videos = data.videos ? data.videos.map((video: any) => new VideoAbstract(video)) : undefined;
    }

    get isAnonymous() {
        return this.realname === '';
    }

    get canSetName() {
        return this.isAnonymous || this.firstname === '' || this.lastname === '';
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

    public newSignatureBudget(newDate: Date) {
        return this.left_signature_n + 12 * (newDate.getUTCFullYear() - this.last_change_avatar.getUTCFullYear()) + (newDate.getUTCMonth() - this.last_change_avatar.getUTCMonth());
    }

    get nextSignatureAvailable() {
        if (this.left_signature_n > 0) return this.last_change_signature;
        const year = this.last_change_avatar.getUTCFullYear();
        const month = this.last_change_avatar.getUTCMonth();
        const targetTimestamp = Date.UTC(year, month + 1, 1, 0, 0, 0, 0);
        return new Date(targetTimestamp);
    }
}
