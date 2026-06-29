import type { AccountLinkPlatform } from './platforms';

export interface AccountLinkQueueResponse {
    id: number;
    platform: AccountLinkPlatform;
    identifier: string;
    userprofile: number;
    verified: boolean;
}
