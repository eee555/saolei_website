import { VideoAbstract } from './videoabstract';

interface UserProfileData {
    [key: string]: unknown;
    id?: number;
    username?: string;
    realname?: string;
    firstname?: string;
    lastname?: string;
    is_banned?: boolean;
    is_staff?: boolean;
    country?: string;
    signature?: string;
    last_change_avatar?: string | Date | null;
    last_change_signature?: string | Date | null;
    left_avatar_n?: number;
    left_signature_n?: number;
    identifiers?: string[];
    videos?: ConstructorParameters<typeof VideoAbstract>[0][];
}

export class UserProfile {
    public id = 0;
    public username = '';
    public realname = '';
    public firstname = '';
    public lastname = '';
    public is_banned = false;
    public is_staff = false;
    public country = '';
    public signature = '';
    public last_change_avatar: Date = new Date();
    public last_change_signature: Date = new Date();
    public left_avatar_n = 0;
    public left_signature_n = 0;
    public accountlink: any[] = [];
    public identifiers?: string[];
    public videos?: VideoAbstract[];

    public constructor(data?: UserProfileData) {
        if (data === undefined) return;
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

        this.last_change_avatar = new Date(data.last_change_avatar ?? Date.now());
        this.last_change_signature = new Date(data.last_change_signature ?? Date.now());

        this.left_avatar_n = data.left_avatar_n ?? 0;
        this.left_signature_n = data.left_signature_n ?? 0;

        this.identifiers = data.identifiers;
        this.videos = data.videos?.map((video) => new VideoAbstract(video));
    }

    public get isAnonymous(): boolean {
        return this.realname === '';
    }

    public get hasInternationalName(): boolean {
        return this.firstname !== '' && this.lastname !== '';
    }

    public get canSetName(): boolean {
        return this.isAnonymous || this.firstname === '' || this.lastname === '';
    }

    public get nextAvatarAvailable(): Date {
        if (this.left_avatar_n > 0) return this.last_change_avatar;
        const year = this.last_change_avatar.getUTCFullYear();
        const targetTimestamp = Date.UTC(year + 1, 0, 1, 0, 0, 0);
        return new Date(targetTimestamp);
    }

    public get nextSignatureAvailable(): Date {
        if (this.left_signature_n > 0) return this.last_change_signature;
        const year = this.last_change_avatar.getUTCFullYear();
        const month = this.last_change_avatar.getUTCMonth();
        const targetTimestamp = Date.UTC(year, month + 1, 1, 0, 0, 0, 0);
        return new Date(targetTimestamp);
    }

    public newAvatarBudget(newDate: Date): number {
        return this.left_avatar_n + newDate.getUTCFullYear() - this.last_change_avatar.getUTCFullYear();
    }

    public newSignatureBudget(newDate: Date): number {
        return this.left_signature_n + 12 * (newDate.getUTCFullYear() - this.last_change_avatar.getUTCFullYear()) + (newDate.getUTCMonth() - this.last_change_avatar.getUTCMonth());
    }
}
