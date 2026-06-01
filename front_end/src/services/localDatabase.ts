import { Dexie } from 'dexie';
import type { EntityTable } from 'dexie';

const databaseName = 'saolei_local';

export type LocalUser = {
    id: number;
    username: string;
    realname: string;
    firstname: string;
    lastname: string;
    is_banned: boolean;
    is_staff: boolean;
    country: string;
    signature: string;
    last_change_avatar: string;
    last_change_signature: string;
    left_avatar_n: number;
    left_signature_n: number;
    updatedAt: number;
};

class SaoleiLocalDatabase extends Dexie {
    users!: EntityTable<LocalUser, 'id'>;

    constructor() {
        super(databaseName);

        this.version(1).stores({
            users: 'id, username, updatedAt',
        });
    }
}

export const localDatabase = new SaoleiLocalDatabase();
