export type MemoryFailureReason = 'permission_denied' | 'unsupported_metric' | 'unsupported_scope' | 'budget_exceeded' | 'metadata_unavailable' | 'inconsistent_snapshot' | 'redis_unavailable' | 'database_unavailable' | 'collection_failed';

export const processMemoryGroups = ['uwsgi', 'apscheduler', 'redis', 'mysql', 'db_worker', 'other'] as const;
export const redisMemoryGroups = ['pb_rankings', 'other_rankings', 'latest_videos', 'other'] as const;

interface MemorySection<K extends string> {
    status: 'ready' | 'unavailable';
    sampled_at: string | null;
    reason: MemoryFailureReason | null;
    total_bytes: number | null;
    groups: Record<K, number> | null;
}

export interface ProcessMemorySection extends MemorySection<typeof processMemoryGroups[number]> {
    metric: 'pss' | 'rss';
    host: { total_bytes: number; available_bytes: number } | null;
    unreadable_processes: number;
}

export interface RedisMemorySection extends MemorySection<typeof redisMemoryGroups[number]> {
    metric: 'redis_allocated';
    estimated: true;
    samples: 5;
}

export interface MemoryUsageResponse {
    memory: ProcessMemorySection;
    redis: RedisMemorySection;
}

export interface MemorySeries {
    key: string;
    name: string;
    value: number;
    color: string;
}

export const memoryColors = ['#409eff', '#e6a23c', '#67c23a', '#f56c6c', '#a879e6', '#909399'];
