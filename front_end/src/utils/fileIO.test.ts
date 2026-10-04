import { afterEach, describe, expect, it, vi } from 'vitest';

import { createDirectoryNewFileEmitter } from './fileIO';
import type { DirectoryNewFileListener } from './fileIO';

class FakeFileHandle {
    public readonly kind = 'file';
    public readonly name: string;
    private readonly file: File;

    public constructor(file: File) {
        this.file = file;
        this.name = file.name;
    }

    public getFile() {
        return Promise.resolve(this.file);
    }
}

class FakeDirectoryHandle {
    public readonly kind = 'directory';
    public readonly name = 'videos';
    private readonly handles = new Map<string, FakeFileHandle | FakeDirectoryHandle>();

    public constructor(files: File[] = []) {
        for (const file of files) {
            this.addFile(file);
        }
    }

    public addFile(file: File) {
        this.handles.set(file.name, new FakeFileHandle(file));
    }

    public addDirectory(name: string) {
        this.handles.set(name, new FakeDirectoryHandle());
    }

    public async *values() {
        await Promise.resolve();
        yield* this.handles.values();
    }
}

function directoryHandle(files: File[] = []) {
    return new FakeDirectoryHandle(files) as unknown as FileSystemDirectoryHandle;
}

describe('DirectoryNewFileEmitter', () => {
    afterEach(() => {
        vi.useRealTimers();
    });

    it('emits files added after start without replaying existing files', async () => {
        const directory = new FakeDirectoryHandle([new File(['old'], 'old.evf')]);
        const emitter = createDirectoryNewFileEmitter(directory as unknown as FileSystemDirectoryHandle, { pollIntervalMs: 100000 });
        const emitted: string[] = [];

        emitter.onFile(({ file }) => {
            emitted.push(file.name);
        });
        await emitter.start();
        directory.addFile(new File(['new'], 'new.evf'));

        const events = await emitter.scan();

        expect(events.map(({ file }) => file.name)).toEqual(['new.evf']);
        expect(emitted).toEqual(['new.evf']);
        expect(await emitter.scan()).toEqual([]);

        emitter.stop();
    });

    it('can emit existing files on start', async () => {
        const emitter = createDirectoryNewFileEmitter(directoryHandle([new File(['video'], 'video.avf')]), {
            emitExisting: true,
            pollIntervalMs: 100000,
        });
        const emitted: string[] = [];

        emitter.onFile(({ file }) => {
            emitted.push(file.name);
        });
        await emitter.start();

        expect(emitted).toEqual(['video.avf']);

        emitter.stop();
    });

    it('resumes with only files added while paused and keeps the original baseline', async () => {
        const directory = new FakeDirectoryHandle([new File(['old'], 'old.evf')]);
        const emitter = createDirectoryNewFileEmitter(directory as unknown as FileSystemDirectoryHandle);
        const listener = vi.fn<DirectoryNewFileListener>();
        emitter.onFile(listener);
        await emitter.start(false);
        emitter.stop();
        directory.addFile(new File(['new'], 'new.evf'));
        await emitter.start(true);
        emitter.stop();
        await emitter.start(true);
        emitter.stop();
        expect(listener).toHaveBeenCalledTimes(1);
        expect(listener.mock.calls[0][0].file.name).toBe('new.evf');
    });

    it('does not restart polling after cancelling an initial scan', async () => {
        vi.useFakeTimers();
        const emitter = createDirectoryNewFileEmitter(directoryHandle([new File(['a'], 'a.evf'), new File(['b'], 'b.evf')]));
        const listener = vi.fn(() => {
            emitter.stop();
        });
        emitter.onFile(listener);
        await emitter.start(true);
        await vi.advanceTimersByTimeAsync(10000);
        expect(listener).toHaveBeenCalledTimes(1);
        expect(emitter.running).toBe(false);
        expect(vi.getTimerCount()).toBe(0);
    });

    it('waits for processing before dispatching the next file and resumes unprocessed files', async () => {
        const emitter = createDirectoryNewFileEmitter(directoryHandle([new File(['a'], 'a.evf'), new File(['b'], 'b.evf')]));
        let release!: () => void;
        const gate = new Promise<void>((resolve) => {
            release = resolve;
        });
        const listener = vi.fn<DirectoryNewFileListener>().mockImplementationOnce(() => gate);
        emitter.onFile(listener);
        const starting = emitter.start(true);
        await vi.waitFor(() => {
            expect(listener).toHaveBeenCalledTimes(1);
        });
        emitter.stop();
        release();
        await starting;
        expect(listener).toHaveBeenCalledTimes(1);
        await emitter.start(true);
        emitter.stop();
        expect(listener).toHaveBeenCalledTimes(2);
        expect(listener.mock.calls[1][0].file.name).toBe('b.evf');
    });

    it('does not create a timer when stopped during baseline enumeration', async () => {
        vi.useFakeTimers();
        const emitter = createDirectoryNewFileEmitter(directoryHandle());
        const starting = emitter.start(false);
        emitter.stop();
        await starting;
        expect(emitter.running).toBe(false);
        expect(vi.getTimerCount()).toBe(0);
    });

    it('ignores child directories', async () => {
        const directory = new FakeDirectoryHandle();
        directory.addDirectory('nested');
        directory.addFile(new File(['video'], 'video.rmv'));
        const emitter = createDirectoryNewFileEmitter(directory as unknown as FileSystemDirectoryHandle);

        const events = await emitter.scan();

        expect(events.map(({ file }) => file.name)).toEqual(['video.rmv']);
    });

    it('polls the directory while running', async () => {
        vi.useFakeTimers();
        const directory = new FakeDirectoryHandle();
        const emitter = createDirectoryNewFileEmitter(directory as unknown as FileSystemDirectoryHandle, { pollIntervalMs: 1000 });
        const emitted: string[] = [];

        emitter.onFile(({ file }) => {
            emitted.push(file.name);
        });
        await emitter.start();
        directory.addFile(new File(['video'], 'video.mvf'));
        await vi.advanceTimersByTimeAsync(1000);

        expect(emitted).toEqual(['video.mvf']);

        emitter.stop();
    });
});
