import { interceptFormData } from 'cypress-intercept-formdata';

import AutoUploader from './AutoUploader.vue';

import i18n from '@/i18n';
import type { VideoUploadResponse } from '@/services/videoUploadService';
import { MS_State } from '@/utils/ms_const';
import { WeeklyParticipant, WeeklyTournamentFormat } from '@/utils/weekly';
import { binaryStringToUint8Array } from '@cy/support/stupidCypress';

const weeklyToken = 'G11479';

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
    private readonly handles = new Map<string, FakeFileHandle>();

    public addFile(file: File) {
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

interface UploadResponseCase {
    label: string;
    responseBody: VideoUploadResponse;
}

function weeklyParticipant(init: Partial<WeeklyParticipant> = {}) {
    return new WeeklyParticipant({
        id: 1147901,
        token: weeklyToken,
        tournament_id: 11479,
        user_id: 101,
        start_time: new Date('2000-01-01T00:00:00+08:00'),
        end_time: new Date('2099-01-01T00:00:00+08:00'),
        rank_score: 0,
        ...init,
    });
}

function mountAutoUploader(options: { participant?: WeeklyParticipant } = {}) {
    return cy.mount(AutoUploader, {
        props: {
            format: WeeklyTournamentFormat.Classic,
            participant: options.participant ?? weeklyParticipant(),
        },
        global: {
            plugins: [i18n],
        },
    });
}

function setDirectoryPicker(directory?: FakeDirectoryHandle) {
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

function setPollInterval(seconds: number) {
    cy.contains('.auto-uploader__control', 'Poll interval').find('input').as('pollIntervalInput');
    cy.get('@pollIntervalInput').clear();
    cy.get('@pollIntervalInput').type(seconds.toString());
}

function loadStandardGSCFile() {
    return cy.fixture('standard_gsc.evf', 'binary').then((fileContent) => {
        const bytes = binaryStringToUint8Array(fileContent);
        const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;
        return new File([buffer], 'standard_gsc.evf');
    });
}

function interceptStandardGSCUpload(responseBody: VideoUploadResponse) {
    cy.intercept('POST', '/common/uploadvideo/', (req) => {
        expect(interceptFormData(req).file).to.equal('standard_gsc.evf');
        req.reply({
            statusCode: 200,
            body: responseBody,
        });
    }).as('uploadRequest');
}

function interceptStandardGSCUploadHttpError(statusCode: number) {
    cy.intercept('POST', '/common/uploadvideo/', (req) => {
        expect(interceptFormData(req).file).to.equal('standard_gsc.evf');
        req.reply({
            statusCode,
            body: {
                detail: 'upload rejected',
            },
        });
    }).as('uploadRequest');
}

function interceptDelayedStandardGSCUpload(responseBody: VideoUploadResponse, gate: Promise<void>) {
    cy.intercept('POST', '/common/uploadvideo/', (req) => {
        expect(interceptFormData(req).file).to.equal('standard_gsc.evf');
        return gate.then(() => {
            req.reply({
                statusCode: 200,
                body: responseBody,
            });
        });
    }).as('uploadRequest');
}

function startWatchingDirectory(directory: FakeDirectoryHandle, participant: WeeklyParticipant) {
    setDirectoryPicker(directory);
    cy.window().then((win) => {
        cy.stub(win.console, 'info').as('consoleInfo');
    });
    mountAutoUploader({
        participant,
    });
    setPollInterval(1);

    cy.contains('button', 'Select folder').should('not.be.disabled').click();
    cy.get('@showDirectoryPicker').should('have.been.calledOnce');
    cy.contains('Watching videos').should('be.visible');
}

function addStandardGSCFile(directory: FakeDirectoryHandle) {
    loadStandardGSCFile().then((file) => {
        directory.addFile(file);
    });
}

function expectUploadFailure(participant: WeeklyParticipant, action: 'upload failed' | 'upload error') {
    cy.contains('Failed: 100%(1)').should('be.visible');
    cy.contains('Uploaded:').should('not.exist');
    cy.contains('Processing:').should('not.exist');
    cy.contains('Skipped:').should('not.exist');
    cy.get('@consoleInfo').should('have.been.calledWithMatch', '[WeeklyAutoUploader]', action);
    cy.then(() => {
        expect(participant.videos).to.be.undefined;
        expect(participant.classic_et).to.deep.equal([[0, 240000], [0, 240000]]);
        expect(participant.classic_score).to.equal(780000);
    });
}

const uploadErrorResponseCases: UploadResponseCase[] = [
    {
        label: 'file collision',
        responseBody: {
            type: 'error',
            object: 'file',
        },
    },
    {
        label: 'identifier censorship',
        responseBody: {
            type: 'error',
            object: 'identifier',
        },
    },
    {
        label: 'generic upload failure',
        responseBody: {
            type: 'error',
            obj: 'userprofile',
            category: 'realname_required',
        },
    },
];

describe('<AutoUploader />', () => {
    afterEach(() => {
        setDirectoryPicker();
    });

    it('disables directory selection when the browser does not support directory handles', () => {
        setDirectoryPicker();
        mountAutoUploader();

        cy.contains('FileSystemDirectoryHandle is not supported by this browser').should('be.visible');
        cy.contains('button', 'Select folder').should('be.disabled');
    });

    it('disables directory selection outside the participant window', () => {
        setDirectoryPicker(new FakeDirectoryHandle());
        mountAutoUploader({
            participant: weeklyParticipant({
                start_time: new Date('2000-01-01T00:00:00+08:00'),
                end_time: new Date('2001-01-01T00:00:00+08:00'),
            }),
        });

        cy.contains('Outside session window').should('be.visible');
        cy.contains('button', 'Select folder').should('be.disabled');
    });

    it('uploads a new supported tournament video and adds it to the participant', () => {
        const directory = new FakeDirectoryHandle();
        const participant = weeklyParticipant();
        const responseBody: VideoUploadResponse = {
            type: 'success',
            object: 'videomodel',
            category: 'upload',
            data: {
                id: 114790101,
                state: MS_State.Official,
            },
        };
        let finishUpload: (() => void) | undefined;
        const uploadGate = new Promise<void>((resolve) => {
            finishUpload = resolve;
        });
        interceptDelayedStandardGSCUpload(responseBody, uploadGate);
        startWatchingDirectory(directory, participant);
        addStandardGSCFile(directory);

        cy.contains('Processing: 100%(1)').should('be.visible').then(() => {
            if (finishUpload === undefined) throw new Error('Upload request was not captured.');
            finishUpload();
        });
        cy.wait('@uploadRequest').its('response.statusCode').should('eq', 200);
        cy.contains('Uploaded: 100%(1)').should('be.visible');
        cy.contains('Processing:').should('not.exist');
        cy.contains('Skipped:').should('not.exist');
        cy.contains('Failed:').should('not.exist');
        cy.get('@consoleInfo').should('have.been.calledWithMatch', '[WeeklyAutoUploader]', 'upload success');
        cy.then(() => {
            expect(participant.videos).to.have.length(1);
            expect(participant.videos?.[0]).to.include({
                id: 114790101,
                state: MS_State.Official,
                level: 'e',
                mode: '00',
                timems: 41021,
            });
            expect(participant.classic_et).to.deep.equal([[114790101, 41021], [0, 240000]]);
            expect(participant.classic_score).to.equal(581021);
        });
    });

    it('adds a successful identifier-state upload to the participant', () => {
        const directory = new FakeDirectoryHandle();
        const participant = weeklyParticipant();
        interceptStandardGSCUpload({
            type: 'success',
            object: 'videomodel',
            category: 'upload',
            data: {
                id: 114790102,
                state: MS_State.Identifier,
            },
        });
        startWatchingDirectory(directory, participant);
        addStandardGSCFile(directory);

        cy.wait('@uploadRequest').its('response.statusCode').should('eq', 200);
        cy.contains('Uploaded: 100%(1)').should('be.visible');
        cy.contains('Processing:').should('not.exist');
        cy.contains('Skipped:').should('not.exist');
        cy.contains('Failed:').should('not.exist');
        cy.get('@consoleInfo').should('have.been.calledWithMatch', '[WeeklyAutoUploader]', 'upload success');
        cy.then(() => {
            expect(participant.videos).to.have.length(1);
            expect(participant.videos?.[0]).to.include({
                id: 114790102,
                state: MS_State.Identifier,
                level: 'e',
                mode: '00',
                timems: 41021,
            });
            expect(participant.classic_et).to.deep.equal([[114790102, 41021], [0, 240000]]);
            expect(participant.classic_score).to.equal(581021);
        });
    });

    uploadErrorResponseCases.forEach(({ label, responseBody }) => {
        it(`marks ${label} responses as failed without adding the video`, () => {
            const directory = new FakeDirectoryHandle();
            const participant = weeklyParticipant();
            interceptStandardGSCUpload(responseBody);
            startWatchingDirectory(directory, participant);
            addStandardGSCFile(directory);

            cy.wait('@uploadRequest').its('response.statusCode').should('eq', 200);
            expectUploadFailure(participant, 'upload failed');
        });
    });

    it('marks non-200 upload responses as failed without adding the video', () => {
        const directory = new FakeDirectoryHandle();
        const participant = weeklyParticipant();
        interceptStandardGSCUploadHttpError(402);
        startWatchingDirectory(directory, participant);
        addStandardGSCFile(directory);

        cy.wait('@uploadRequest').its('response.statusCode').should('eq', 402);
        expectUploadFailure(participant, 'upload error');
    });
});
