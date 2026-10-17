import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { cropPixels, exportBoardVideo, exportTiming } from './videoExport';
import type { VideoExportOptions } from './videoExport';

const sdk = vi.hoisted(() => ({
    codecs: vi.fn(), canEncode: vi.fn(), source: vi.fn(), start: vi.fn(), add: vi.fn(), finalize: vi.fn(), cancel: vi.fn(), close: vi.fn(), addTrack: vi.fn(),
}));
vi.mock('mediabunny', () => {
    class BufferTarget {
        public buffer: ArrayBuffer | null = null;
    }
    class Output {
        public target: BufferTarget;
        public start = sdk.start;
        public cancel = sdk.cancel;
        public addVideoTrack = sdk.addTrack;
        public constructor(options: { target: BufferTarget }) {
            this.target = options.target;
        }

        public async finalize() {
            await sdk.finalize();
            this.target.buffer = new ArrayBuffer(4);
        }
    }
    class CanvasSource {
        public add = sdk.add; public close = sdk.close;
        public constructor(canvas: HTMLCanvasElement, config: unknown) {
            sdk.source(canvas, config);
        }
    }
    class Format {
        public mimeType = 'video/mp4';
        public codecs = ['avc', 'vp9'];
        public getSupportedVideoCodecs() {
            return this.codecs;
        }
    }
    class Quality {
        public value: string;
        public constructor(value: string) {
            this.value = value;
        }
    }
    return { Output, BufferTarget, CanvasSource, Quality, Mp4OutputFormat: Format, WebMOutputFormat: Format, MovOutputFormat: Format, MkvOutputFormat: Format, canEncodeVideo: sdk.canEncode, getEncodableVideoCodecs: sdk.codecs };
});

beforeEach(() => {
    vi.clearAllMocks();
    sdk.codecs.mockResolvedValue(['avc']);
    sdk.canEncode.mockResolvedValue(true);
    sdk.add.mockResolvedValue(undefined);
    sdk.finalize.mockResolvedValue(undefined);
    sdk.cancel.mockResolvedValue(undefined);
});
afterEach(() => vi.restoreAllMocks());

function setup(overrides: Partial<VideoExportOptions> = {}) {
    const controller = new AbortController();
    const options: VideoExportOptions = {
        format: 'mp4',
        fps: 10,
        quality: 'high',
        canvas: { width: 64, height: 32 } as HTMLCanvasElement,
        startMs: 500,
        endMs: 1550,
        rate: 2,
        signal: controller.signal,
        render: vi.fn().mockResolvedValue(undefined),
        onProgress: vi.fn<(completed: number, total: number) => void>(),
        ...overrides,
    };
    return { controller, options };
}

describe('board video export', () => {
    it('uses inclusive cell boundaries, including fractional sizes and single cells', () => {
        expect(cropPixels({ top: 0, bottom: 2, left: 0, right: 3 }, 3, 4, 16)).toEqual({ x: 0, y: 0, width: 64, height: 48 });
        expect(cropPixels({ top: 1, bottom: 1, left: 2, right: 2 }, 3, 4, 16.4)).toEqual({ x: 33, y: 16, width: 16, height: 17 });
        for (const crop of [{ top: -1, bottom: 2, left: 0, right: 3 }, { top: 0, bottom: 3, left: 0, right: 3 }, { top: 2, bottom: 1, left: 0, right: 3 }, { top: 0, bottom: 2, left: 1.5, right: 3 }, { top: 0, bottom: 2, left: 3, right: 2 }]) expect(() => cropPixels(crop, 3, 4, 16)).toThrow('Invalid board export region');
    });

    it('rejects zero-length ranges and invalid timing', () => {
        expect(exportTiming(1000, 2000, 2, 30)).toEqual({ duration: 0.5, frameCount: 15 });
        for (const args of [[0, 0, 1, 30], [-1, 10, 1, 30], [0, 10, 0, 30], [0, 10, 1, 0], [0, Infinity, 1, 30], [0, 10, 1, 121]]) expect(() => exportTiming(args[0], args[1], args[2], args[3])).toThrow('Invalid export timing');
    });

    it('submits bounded frames with explicit output timestamps, speed and a shortened final duration', async () => {
        const { options } = setup();
        const blob = await exportBoardVideo(options);
        expect(blob.type).toBe('video/mp4');
        expect(blob.size).toBe(4);
        expect(sdk.canEncode).toHaveBeenCalledWith('avc', expect.objectContaining({ width: 64, height: 32, frameRate: 10, hardwareAcceleration: 'prefer-hardware', latencyMode: 'quality' }));
        expect(sdk.source).toHaveBeenCalledWith(options.canvas, expect.objectContaining({ codec: 'avc', hardwareAcceleration: 'prefer-hardware', latencyMode: 'quality' }));
        expect(vi.mocked(options.render).mock.calls.map(([ms]) => ms)).toEqual([500, 700, 900, 1100, 1300, 1500]);
        expect(sdk.add.mock.calls.slice(0, 5)).toEqual([[0, 0.1], [0.1, 0.1], [0.2, 0.1], [0.3, 0.1], [0.4, 0.1]]);
        expect(sdk.add.mock.calls[5][0]).toBe(0.5);
        expect(sdk.add.mock.calls[5][1]).toBeCloseTo(0.025);
        expect(options.onProgress).toHaveBeenLastCalledWith(6, 6);
        expect(sdk.finalize).toHaveBeenCalledOnce();
        expect(sdk.cancel).not.toHaveBeenCalled();
        expect(sdk.close).toHaveBeenCalledOnce();
    });

    it('applies backpressure before capturing the next frame', async () => {
        let release: (() => void) | undefined;
        sdk.add.mockImplementationOnce(() => new Promise<void>((resolve) => {
            release = resolve;
        }));
        const { options } = setup();
        const promise = exportBoardVideo(options);
        await vi.waitFor(() => {
            expect(sdk.add).toHaveBeenCalledOnce();
        });
        expect(options.render).toHaveBeenCalledOnce();
        release?.();
        await promise;
        expect(options.render).toHaveBeenCalledTimes(6);
    });

    it('rejects unsupported encoders before rendering', async () => {
        sdk.canEncode.mockResolvedValue(false);
        sdk.codecs.mockResolvedValue([]);
        const { options } = setup();
        await expect(exportBoardVideo(options)).rejects.toThrow('No supported MP4 video encoder');
        expect(options.render).not.toHaveBeenCalled();
    });

    it('prefers a later hardware codec over an earlier software codec and falls back when needed', async () => {
        sdk.canEncode.mockImplementation((codec: string) => Promise.resolve(codec === 'vp9'));
        const { options } = setup();
        await exportBoardVideo(options);
        expect(sdk.source).toHaveBeenLastCalledWith(options.canvas, expect.objectContaining({ codec: 'vp9', hardwareAcceleration: 'prefer-hardware' }));
        expect(sdk.codecs).not.toHaveBeenCalled();
        sdk.canEncode.mockResolvedValue(false);
        await exportBoardVideo(options);
        expect(sdk.source).toHaveBeenLastCalledWith(options.canvas, expect.objectContaining({ codec: 'avc', hardwareAcceleration: 'no-preference', latencyMode: 'quality' }));
    });

    it('renders a long video without advancing the wall clock to its playback duration', async () => {
        vi.spyOn(performance, 'now').mockReturnValue(0);
        const timer = vi.spyOn(globalThis, 'setTimeout');
        const { options } = setup({ startMs: 0, endMs: 60000, fps: 1, rate: 1 });
        await exportBoardVideo(options);
        expect(sdk.add).toHaveBeenCalledTimes(60);
        expect(sdk.add).toHaveBeenLastCalledWith(59, 1);
        expect(timer).not.toHaveBeenCalled();
    });

    it('cancels without finalizing or submitting the aborted frame', async () => {
        const { controller, options } = setup();
        options.render = vi.fn(() => {
            controller.abort();
            return Promise.resolve();
        });
        await expect(exportBoardVideo(options)).rejects.toMatchObject({ name: 'AbortError' });
        expect(sdk.cancel).toHaveBeenCalledOnce();
        expect(sdk.add).not.toHaveBeenCalled();
        expect(sdk.finalize).not.toHaveBeenCalled();
        expect(sdk.close).toHaveBeenCalledOnce();
    });

    it('yields to cancellation events even when cached rendering and encoding resolve immediately', async () => {
        let clock = 0;
        vi.spyOn(performance, 'now').mockImplementation(() => clock += 100);
        const { options, controller } = setup();
        options.onProgress = () => {
            setTimeout(() => {
                controller.abort();
            }, 0);
        };
        await expect(exportBoardVideo(options)).rejects.toMatchObject({ name: 'AbortError' });
        expect(sdk.add).toHaveBeenCalledOnce();
        expect(sdk.cancel).toHaveBeenCalledOnce();
        expect(sdk.finalize).not.toHaveBeenCalled();
    });

    it('cleans up rendering and finalization failures', async () => {
        const { options } = setup();
        options.render = vi.fn().mockRejectedValue(new Error('Capture failed'));
        await expect(exportBoardVideo(options)).rejects.toThrow('Capture failed');
        expect(sdk.cancel).toHaveBeenCalledOnce();
        expect(sdk.close).toHaveBeenCalledOnce();
        sdk.finalize.mockRejectedValue(new Error('Encoder failed'));
        options.render = vi.fn().mockResolvedValue(undefined);
        await expect(exportBoardVideo(options)).rejects.toThrow('Encoder failed');
        expect(sdk.cancel).toHaveBeenCalledTimes(2);
    });
});
