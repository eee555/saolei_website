import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { performance } from 'node:perf_hooks';

import { AvfVideo, EvfVideo, MvfVideo, RmvVideo } from 'ms-toollib';

const fixtures = [
    [EvfVideo, '52200.evf'],
    [EvfVideo, 'c_10_129.073_24_0.186_Pu Tian Yi(Hu Bei).evf'],
    [EvfVideo, 'c_10_39.832_24_0.477_Pu Tian Yi(Hu Bei)_fail.evf'],
    [EvfVideo, 'standard_gsc.evf'],
    [AvfVideo, 'Exp_FL_35.09_3BV=132_3BVs=3.76_Pu Tian Yi(Hu Bei).avf'],
    [MvfVideo, 'Lin_Jin_Fan_Exp_60.623bv207.mvf'],
    [RmvVideo, '3819-Time-1616-NF-9469-32-20151031.rmv'],
];
const number = (value) => Number.isFinite(value) ? value : String(value);
function readPluckSeries(video, eventCount) {
    const savedIndex = video.current_event_id;
    try {
        return Array.from({ length: eventCount }, (_, eventIndex) => {
            video.current_event_id = eventIndex;
            return video.pluck;
        });
    } finally {
        video.current_event_id = savedIndex;
    }
}
for (const [Video, filename] of fixtures) {
    const bytes = new Uint8Array(readFileSync(new URL(`../cypress/fixtures/${filename}`, import.meta.url)));
    const video = new Video(bytes, filename);
    let oldRecords = [];
    let records = [];
    try {
        const parseStart = performance.now();
        video.parse();
        video.analyse();
        const parseMs = performance.now() - parseStart;
        oldRecords = video.events;
        video.current_time = 2;
        const index = video.current_event_id;
        const board = video.game_board;
        const beforePluck = video.pluck;
        assert.equal(Number.isNaN(beforePluck), true);
        const featureStart = performance.now();
        assert.equal(video.analyse_for_features(['pluck']), undefined);
        const pluckMs = Math.round((performance.now() - featureStart) * 100) / 100;
        assert.equal(video.current_event_id, index);
        assert.deepEqual(video.game_board, board);
        records = video.events;
        assert.equal(records.length, oldRecords.length);
        const params = records.at(-1).key_dynamic_params;
        let exposedParams;
        try {
            exposedParams = Object.getOwnPropertyNames(Object.getPrototypeOf(params)).filter((key) => !key.startsWith('__'));
            assert.equal('pluck' in params, false);
        } finally {
            params.free();
        }
        assert.deepEqual(records.map((record) => record.comments), oldRecords.map((record) => record.comments));
        const pluckAtTwoSeconds = video.pluck;
        const series = readPluckSeries(video, records.length);
        assert.equal(video.current_event_id, index);
        assert.deepEqual(video.game_board, board);
        assert.equal(series.every((value) => Number.isFinite(value)), true);
        const nonzero = series.findIndex((value) => value !== 0);
        const samples = nonzero < 0 ? [] : series.slice(Math.max(0, nonzero - 2), nonzero + 3).map(number);
        const getterStart = performance.now();
        assert.deepEqual(readPluckSeries(video, records.length), series);
        const readSeriesMs = Math.round((performance.now() - getterStart) * 100) / 100;
        video.analyse_for_features(['pluck']);
        assert.deepEqual(readPluckSeries(video, records.length), series);
        console.log(JSON.stringify({ filename, size: [video.row, video.column], duration: video.rtime, events: records.length, parseMs: Math.round(parseMs * 100) / 100, pluckMs, beforePluck: number(beforePluck), pluckAtTwoSeconds: number(pluckAtTwoSeconds), finalPluck: number(series.at(-1)), nonzero, samples, readSeriesMs, exposedParams }));
    } finally {
        for (const record of oldRecords) record.free();
        for (const record of records) record.free();
        video.free();
    }
}
