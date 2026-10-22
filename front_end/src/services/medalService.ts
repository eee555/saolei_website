import $axios from '@/http';
import en from '@/i18n/locales/en';
import zhCn from '@/i18n/locales/zh-cn';

export interface MedalItem {
    code: string;
    series: string;
    subseries: string;
    kind: string;
    stage: number | null;
    stage_count: number;
    direction: 'asc' | 'desc';
    current_value: number | null;
    next_threshold: number | null;
    granted_at: string | null;
    video_id: number | null;
    tournament_id: number | null;
    rank: number | null;
    hidden: boolean;
    annotation: string;
    score: number;
    grant_id: number | null;
    scope_key: string;
    thresholds: number[];
}

export interface PlayerMedals {
    score: number;
    max_pins: number;
    pin_ids: number[];
    pins: MedalItem[];
    series: { series: string; items: MedalItem[] }[];
}

const pinListeners = new Set<() => void>();

export function subscribeMedalPins(listener: () => void): () => void {
    pinListeners.add(listener);
    return () => {
        pinListeners.delete(listener);
    };
}

export function notifyMedalPinsChanged(): void {
    pinListeners.forEach((listener) => {
        listener();
    });
}

export async function fetchPlayerMedals(userId: number): Promise<PlayerMedals> {
    const { data } = await $axios.get<PlayerMedals>(`/api/medal/players/${userId}`);
    return data;
}

export async function saveMedalPins(grantIds: number[]): Promise<void> {
    // 保持默认的表单 Content-Type。带 cookie 时，application/json 的跨域预检会被 Access-Control-Allow-Headers: * 拦住。
    await $axios.put('/api/medal/pins', JSON.stringify({ grant_ids: grantIds }));
    notifyMedalPinsChanged();
}

const medalSeriesKeys: Record<string, keyof typeof en.medal.series> = {
    破境: 'breakthrough',
    神速: 'speed',
    通明: 'mastery',
    盲扫破境: 'flaglessBreakthrough',
    盲扫神速: 'flaglessSpeed',
    盲扫通明: 'flaglessMastery',
    盲扫·精工: 'flaglessPrecision',
    标旗·精工: 'flaggedPrecision',
    三阶盲扫·精工: 'threeTierFlaglessPrecision',
    三阶标旗·精工: 'threeTierFlaggedPrecision',
    实名在册: 'registered',
    录像过审: 'reviewed',
    扫雷新秀: 'firstGlimpse',
    盲扫新秀: 'anotherPath',
    走马观花: 'grandTour',
    旧迹新篇: 'oldTraces',
    原始股东: 'shareholder',
};

export function medalSeriesLabel(series: string, locale: string): string {
    const key = medalSeriesKeys[series];
    if (!key) return series;
    return (locale.startsWith('zh') ? zhCn.medal.series : en.medal.series)[key];
}

const timeSeries = new Set(['破境', '盲扫破境']);
const speedSeries = new Set(['神速', '盲扫神速']);
const precisionSeries = new Set(['盲扫·精工', '标旗·精工', '三阶盲扫·精工', '三阶标旗·精工']);
const noviceSeries = new Set(['实名在册', '录像过审', '扫雷新秀', '盲扫新秀', '走马观花', '旧迹新篇']);

function trimScaled(stage: number, scale: number) {
    return (stage / scale).toFixed(5).replace(/0+$/, '').replace(/\.$/, '');
}

export function medalStageLabel(series: string, stage: number | null): string {
    if (stage == null || noviceSeries.has(series)) return '';
    if (timeSeries.has(series)) return `${zhCn.medal.sub}${stage / 1000}`;
    if (speedSeries.has(series)) return trimScaled(stage, 10000);
    if (precisionSeries.has(series)) return trimScaled(stage, 100000);
    return String(stage);
}

export function medalLevel(code: string): 'b' | 'i' | 'e' | '' {
    const matched = (/\.([bie])$/).exec(code);
    if (matched?.[1] === 'b' || matched?.[1] === 'i' || matched?.[1] === 'e') return matched[1];
    return '';
}

const medalArtFolder: Record<string, string> = {
    破境: 'breakthrough',
    神速: 'speed',
    通明: 'mastery',
    盲扫破境: 'breakthrough-nf',
    盲扫神速: 'speed-nf',
    盲扫通明: 'mastery-nf',
    盲扫·精工: 'precision-nf',
    标旗·精工: 'precision',
    三阶盲扫·精工: 'precision-nf-three',
    三阶标旗·精工: 'precision-three',
    实名在册: 'registered',
    录像过审: 'reviewed',
    扫雷新秀: 'levels',
    盲扫新秀: 'levels-nf',
    走马观花: 'modes',
    旧迹新篇: 'saolei',
    原始股东: 'shareholder',
};

export function medalArtUrl(series: string, code: string, stage: number | null): string | undefined {
    const folder = medalArtFolder[series];
    if (!folder || stage == null) return undefined;
    const level = medalLevel(code);
    const file = level ? `${level}/${stage}.webp` : `${stage}.webp`;
    return `${import.meta.env.BASE_URL}assets/medals/${folder}/${file}`;
}
