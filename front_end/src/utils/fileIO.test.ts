import { afterEach, describe, expect, it, vi } from 'vitest';

import { createDirectoryNewFileEmitter } from './fileIO';

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
