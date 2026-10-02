import $axios from '@/http';

export interface CustomPluckRecord {
    level: string;
    video_id: number;
    pluck: number;
}

export async function fetchCustomPluckPlayerRecords(userId: number): Promise<CustomPluckRecord[]> {
    const { data } = await $axios.get<CustomPluckRecord[]>('/api/customranking/pluck/player', {
        params: { player_id: userId },
    });
    return data;
}
