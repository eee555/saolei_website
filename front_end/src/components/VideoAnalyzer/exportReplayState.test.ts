import { readFileSync } from 'node:fs';

import { describe, expect, it } from 'vitest';

import { createExportStateReader } from './exportReplayState';
import type { ExportBoardSettings } from './exportReplayState';
import { defaultMouseTraceAppearance, mouseTraceAppearanceProps } from './mouseTrace';
import { readReplayCursor } from './replayCursor';
import { mouseTraceRange, readMouseTrace } from './replayMouseTrace';
import { parseReplay } from './replayParser';

describe('export replay positioning', () => {
    for (const [filename, software] of [
        ['52200.evf', 'e'],
        ['c_10_39.832_24_0.477_Pu Tian Yi(Hu Bei)_fail.evf', 'e'],
        ['Exp_FL_35.09_3BV=132_3BVs=3.76_Pu Tian Yi(Hu Bei).avf', 'a'],
        ['Lin_Jin_Fan_Exp_60.623bv207.mvf', 'm'],
        ['3819-Time-1616-NF-9469-32-20151031.rmv', 'r'],
    ] as const) {
        it(`preserves layers, cursor hotspots and history on forward and backward seeks in ${filename}`, () => {
            const bytes = Uint8Array.from(readFileSync(new URL(`../../../cypress/fixtures/${filename}`, import.meta.url))).buffer;
            const replay = parseReplay(bytes, filename, software);
            try {
                const events = readMouseTrace(replay);
                const settings: ExportBoardSettings = { size: 16.4, globalVisible: true, probabilityVisible: true, traceVisible: true, globalOpacity: 0.5, probabilityOpacity: 0.6, traceOpacity: 0.7, traceTailSeconds: 1, trace: { ...mouseTraceAppearanceProps(defaultMouseTraceAppearance()), opacity: 0.25 }, probabilityColors: { colors: ['#000', '#fff'], thresholds: [50] }, cursor: { size: 32, anchor: { x: 3 / 32, y: 2 / 32 } } };
                const read = createExportStateReader(replay, settings, events);
                for (const ms of [2000, replay.rtime_ms, 500]) {
                    const state = read(ms);
                    expect(state.input.board).toEqual(replay.game_board);
                    expect(state.globalBoard).toEqual(replay.board);
                    expect(state.input.layers?.probability).toMatchObject({ board: replay.game_board_poss });
                    expect(state.input.layers?.mouseTrace).toMatchObject({ ...mouseTraceRange(events, ms, 1, replay.current_event_id), events, opacity: 0.25 });
                    const position = readReplayCursor(replay);
                    expect(state.cursor).toEqual(position === null ? null : { x: position.columnIndex * 16.4 - 3, y: position.rowIndex * 16.4 - 2, size: 32 });
                }
                const hidden = createExportStateReader(replay, { ...settings, globalVisible: false, probabilityVisible: false, traceVisible: false, cursor: null }, events)(1000);
                expect(hidden.globalBoard).toBeNull();
                expect(hidden.cursor).toBeNull();
                expect(hidden.input.layers).toEqual({ probability: false, mouseTrace: false });
            } finally {
                replay.free();
            }
        });
    }
});
