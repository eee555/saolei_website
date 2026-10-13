export const videoFormats = ['mp4', 'webm', 'mov', 'mkv'] as const;
export type VideoFormat = typeof videoFormats[number];
export const videoQualities = ['low', 'medium', 'high', 'very-high'] as const;
export type VideoQuality = typeof videoQualities[number];

export interface VideoExportSettings {
    format: VideoFormat;
    fps: number;
    quality: VideoQuality;
}

export interface BoardCrop {
    top: number;
    bottom: number;
    left: number;
    right: number;
}

export function cropPixels(crop: BoardCrop, rows: number, columns: number, cellSize: number): { x: number; y: number; width: number; height: number } {
    if (!Number.isFinite(cellSize) || cellSize <= 0) throw new Error('Invalid board cell size');
    if (!Object.values(crop).every(Number.isInteger) || crop.top < 0 || crop.left < 0 || crop.bottom >= rows || crop.right >= columns || crop.top > crop.bottom || crop.left > crop.right) throw new Error('Invalid board export region');
    const x = Math.round(crop.left * cellSize);
    const y = Math.round(crop.top * cellSize);
    const width = Math.round((crop.right + 1) * cellSize) - x;
    const height = Math.round((crop.bottom + 1) * cellSize) - y;
    if (width < 1 || height < 1) throw new Error('Export region is smaller than one pixel');
    return { x, y, width, height };
}

export function exportTiming(startMs: number, endMs: number, rate: number, fps: number): { duration: number; frameCount: number } {
    if (![startMs, endMs, rate, fps].every(Number.isFinite) || startMs < 0 || endMs <= startMs || rate <= 0 || fps <= 0 || fps > 120) throw new Error('Invalid export timing');
    const duration = (endMs - startMs) / (rate * 1000);
    return { duration, frameCount: Math.ceil((endMs - startMs) * fps / (rate * 1000)) };
}

export interface VideoExportOptions extends VideoExportSettings {
    canvas: HTMLCanvasElement;
    startMs: number;
    endMs: number;
    rate: number;
    signal: AbortSignal;
    render: (replayMs: number) => Promise<void>;
    onProgress: (completed: number, total: number) => void;
}

export async function exportBoardVideo(options: VideoExportOptions): Promise<Blob> {
    const { duration, frameCount } = exportTiming(options.startMs, options.endMs, options.rate, options.fps);
    options.signal.throwIfAborted();
    const { Output, BufferTarget, CanvasSource, Quality, Mp4OutputFormat, WebMOutputFormat, MovOutputFormat, MkvOutputFormat, canEncodeVideo, getEncodableVideoCodecs } = await import('mediabunny');
    options.signal.throwIfAborted();
    const format = { mp4: () => new Mp4OutputFormat(), webm: () => new WebMOutputFormat(), mov: () => new MovOutputFormat(), mkv: () => new MkvOutputFormat() }[options.format]();
    const quality = new Quality(options.quality);
    const config = { width: options.canvas.width, height: options.canvas.height, frameRate: options.fps, quality, latencyMode: 'quality' as const };
    let hardwareAcceleration: 'prefer-hardware' | 'no-preference' = 'prefer-hardware';
    const supportedCodecs = format.getSupportedVideoCodecs();
    const hardwareSupport = await Promise.all(supportedCodecs.map((codec) => canEncodeVideo(codec, { ...config, hardwareAcceleration })));
    let codec = supportedCodecs.find((_codec, index) => hardwareSupport[index]);
    options.signal.throwIfAborted();
    if (codec === undefined) {
        hardwareAcceleration = 'no-preference';
        [codec] = await getEncodableVideoCodecs(supportedCodecs, config);
    }
    options.signal.throwIfAborted();
    if (codec === undefined) throw new Error(`No supported ${options.format.toUpperCase()} video encoder for ${options.canvas.width} x ${options.canvas.height} at ${options.fps} FPS`);
    const target = new BufferTarget();
    const output = new Output({ format, target });
    const source = new CanvasSource(options.canvas, { codec, quality, hardwareAcceleration, latencyMode: 'quality' });
    // Observe cancellation errors immediately, even while a frame is being rendered.
    let cancellation: Promise<void> | undefined;
    const cancel = () => {
        cancellation ??= output.cancel();
        void cancellation.catch(() => undefined);
    };
    options.signal.addEventListener('abort', cancel, { once: true });
    try {
        output.addVideoTrack(source, { frameRate: options.fps });
        options.signal.throwIfAborted();
        await output.start();
        let lastYield = performance.now();
        for (let index = 0; index < frameCount; index++) {
            options.signal.throwIfAborted();
            const timestamp = index / options.fps;
            await options.render(options.startMs + timestamp * options.rate * 1000);
            options.signal.throwIfAborted();
            await source.add(timestamp, Math.min(1 / options.fps, duration - timestamp));
            // Refresh progress at most every 50ms, not on each encoded frame.
            if (index + 1 === frameCount || performance.now() - lastYield >= 50) {
                options.onProgress(index + 1, frameCount);
                // Cached rendering can resolve entirely in microtasks. Let cancel clicks run.
                if (index + 1 < frameCount) {
                    await new Promise<void>((resolve) => {
                        setTimeout(resolve, 0);
                    });
                    lastYield = performance.now();
                }
            }
        }
        options.signal.throwIfAborted();
        await output.finalize();
        options.signal.throwIfAborted();
        if (target.buffer === null) throw new Error('Video encoder returned no output');
        return new Blob([target.buffer], { type: format.mimeType });
    } catch (error) {
        cancel();
        await cancellation?.catch(() => undefined);
        throw error;
    } finally {
        options.signal.removeEventListener('abort', cancel);
        source.close();
    }
}

