import { defaultBoardEventSettings } from './boardEvents';
import type { BoardEventSettings } from './boardEvents';
import { defaultCounterConfig } from './counter';
import type { CounterConfig } from './counter';
import { defaultCustomEvent } from './customEvents';
import type { CustomEventDefinition } from './customEvents';
import { defaultMouseTraceAppearance } from './mouseTrace';
import type { MouseTraceAppearance } from './mouseTrace';
import { defaultTimelineConfig } from './timeline';
import type { TimelineConfig } from './timeline';
import type { LoopMode } from './usePlayback';
import type { VideoExportSettings } from './videoExport';

export const layouts = ['counter-left', 'counter-right', 'counter-top', 'board-top'] as const;
export type AnalyzerLayout = typeof layouts[number];
export type CellSizeMode = 'fixed' | 'relative' | 'auto';
export type CursorShape = 'dot' | 'windows' | 'ring' | 'crosshair';

export interface AnalyzerConfig {
    selectedLayout: AnalyzerLayout | 'auto';
    panelSizes: Record<AnalyzerLayout, { outer: number[]; upper: number[] }>;
    globalVisible: boolean;
    probabilityVisible: boolean;
    globalOpacity: number;
    probabilityOpacity: number;
    traceVisible: boolean;
    traceOpacity: number;
    traceTailSeconds: number | 'infinite';
    traceMaskOpacity: number;
    traceAppearance: MouseTraceAppearance;
    playbackRate: number;
    loopMode: LoopMode;
    cellSizeMode: CellSizeMode;
    fixedCellSize: number;
    cellScale: number;
    cursorVisible: boolean;
    cursorShape: CursorShape;
    cursorSize: number;
    counter: CounterConfig;
    timeline: TimelineConfig;
    customEvents: CustomEventDefinition[];
    eventLayer: BoardEventSettings;
    videoExport: VideoExportSettings;
}

export function defaultAnalyzerConfig(): AnalyzerConfig {
    return {
        selectedLayout: 'auto',
        panelSizes: {
            'counter-left': { outer: [75, 25], upper: [30, 70] },
            'counter-right': { outer: [75, 25], upper: [70, 30] },
            'counter-top': { outer: [25, 50, 25], upper: [] },
            'board-top': { outer: [50, 25, 25], upper: [] },
        },
        globalVisible: false,
        probabilityVisible: true,
        globalOpacity: 1,
        probabilityOpacity: 1,
        traceVisible: false,
        traceOpacity: 1,
        traceTailSeconds: 1,
        traceMaskOpacity: 0.5,
        traceAppearance: defaultMouseTraceAppearance(),
        playbackRate: 1,
        loopMode: 'none',
        cellSizeMode: 'auto',
        fixedCellSize: 32,
        cellScale: 1,
        cursorVisible: true,
        cursorShape: 'dot',
        cursorSize: 32,
        counter: defaultCounterConfig(),
        timeline: defaultTimelineConfig(),
        customEvents: [
            { ...defaultCustomEvent(), key: 'left', expression: 'mouse_state in [4, 5, 6, 7]', type: 'sustained' },
            { ...defaultCustomEvent(), key: 'right', expression: 'mouse_state in [2, 3, 5, 6]', type: 'sustained' },
        ],
        eventLayer: defaultBoardEventSettings(),
        videoExport: { format: 'mp4', fps: 30, quality: 'high' },
    };
}

