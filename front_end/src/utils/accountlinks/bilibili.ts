export interface AccountBilibiliResponse {
    id: number;
    parent: number;
    update_time: string;
    name: string;
    face: string;
    sign: string;
    level: number;
    following: number;
    follower: number;
    video_count: number;
    article_count: number;
    opus_count: number;
    official_title: string;
}

export class AccountBilibili {
    public id = 0;
    public update_time = new Date(0);
    public name = '';
    public face = '';
    public sign = '';
    public level = 0;
    public following = 0;
    public follower = 0;
    public video_count = 0;
    public article_count = 0;
    public opus_count = 0;
    public official_title = '';

    public constructor(data?: AccountBilibiliResponse) {
        if (data === undefined) return;

        this.id = data.id;
        this.update_time = new Date(data.update_time);
        this.name = data.name;
        this.face = data.face;
        this.sign = data.sign;
        this.level = data.level;
        this.following = data.following;
        this.follower = data.follower;
        this.video_count = data.video_count;
        this.article_count = data.article_count;
        this.opus_count = data.opus_count;
        this.official_title = data.official_title;
    }
}
