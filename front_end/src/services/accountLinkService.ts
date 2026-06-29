import $axios from '@/http';
import { AccountLinks } from '@/utils/accountlinks';
import type { AccountLinkPlatform, AccountLinkQueueResponse, AccountLinksResponse } from '@/utils/accountlinks';

export async function fetchAccountLinks(userId: number): Promise<AccountLinks> {
    const { data } = await $axios.get(`/api/accountlink/${userId}`);
    return new AccountLinks(data as AccountLinksResponse);
}

export async function addAccountLink(platform: AccountLinkPlatform, identifier: string): Promise<AccountLinkQueueResponse> {
    const { data } = await $axios.post('/api/accountlink/create/', {
        platform,
        identifier,
    });
    return data as AccountLinkQueueResponse;
}
