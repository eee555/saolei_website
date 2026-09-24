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

export class FakeDirectoryHandle {
    public readonly kind = 'directory';
    public readonly name = 'videos';
    private readonly handles = new Map<string, FakeFileHandle>();

    public addFile(file: File): void {
        this.handles.set(file.name, new FakeFileHandle(file));
    }

    public async *values(): AsyncGenerator<FakeFileHandle, void, unknown> {
        await Promise.resolve();
        yield* this.handles.values();
    }
}

interface DirectoryPickerWindow extends Window {
    showDirectoryPicker?: (options?: { mode?: 'read' | 'readwrite' }) => Promise<FileSystemDirectoryHandle>;
}

export function setDirectoryPicker(directory?: FakeDirectoryHandle): void {
    cy.window().then((win) => {
        const pickerWindow = win as DirectoryPickerWindow;
        if (directory === undefined) {
            Object.defineProperty(pickerWindow, 'showDirectoryPicker', { configurable: true, value: undefined });
            return;
        }
        const picker = cy.stub().resolves(directory);
        Object.defineProperty(pickerWindow, 'showDirectoryPicker', { configurable: true, value: picker });
        cy.wrap(picker).as('showDirectoryPicker');
    });
}

export function setPollInterval(seconds: number): void {
    cy.contains('.auto-uploader__control', 'Poll interval').find('input').as('pollIntervalInput');
    cy.get('@pollIntervalInput').clear();
    cy.get('@pollIntervalInput').type(seconds.toString());
}
