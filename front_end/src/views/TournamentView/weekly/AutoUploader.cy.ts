import { interceptFormData } from 'cypress-intercept-formdata';

import AutoUploader from './AutoUploader.vue';

import i18n from '@/i18n';
import { MS_State, TournamentState, TournamentSubclass } from '@/utils/ms_const';
import { Tournament, TournamentParticipant } from '@/utils/tournaments';
import type { VideoAbstract } from '@/utils/videoabstract';
import { WeeklyTournamentFormat } from '@/utils/weekly';
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

function weeklyTournament() {
    return new Tournament({
        id: 11479,
        subclass: TournamentSubclass.Weekly,
        data: {
            year: 2099,
            week: 1,
            tournament_format: WeeklyTournamentFormat.Classic,
        },
        start_time: '2000-01-01T00:00:00+08:00',
        end_time: '2099-01-01T00:00:00+08:00',
        state: TournamentState.Normal,
    });
}

function weeklyParticipant(init: Partial<TournamentParticipant> = {}) {
    return new TournamentParticipant({
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

function mountAutoUploader(options: { participant?: TournamentParticipant; videos?: VideoAbstract[] } = {}) {
    return cy.mount(AutoUploader, {
        props: {
            tournament: weeklyTournament(),
            participant: options.participant,
            videos: options.videos ?? [],
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

describe('<AutoUploader />', () => {
    afterEach(() => {
        setDirectoryPicker();
    });

    it('disables directory selection when the browser does not support directory handles', () => {
        setDirectoryPicker();
        mountAutoUploader({
            participant: weeklyParticipant(),
        });

        cy.contains('Directory watching is not supported').should('be.visible');
        cy.contains('button', 'Select folder').should('be.disabled');
    });

    it('disables directory selection before the user registers', () => {
        setDirectoryPicker(new FakeDirectoryHandle());
        mountAutoUploader();

        cy.contains('Not registered').should('be.visible');
        cy.contains('button', 'Select folder').should('be.disabled');
    });

    it('uploads a new supported tournament video and emits the uploaded video', () => {
        const directory = new FakeDirectoryHandle();
        setDirectoryPicker(directory);
        cy.window().then((win) => {
            cy.stub(win.console, 'info').as('consoleInfo');
        });
        cy.intercept('POST', '/common/uploadvideo/', (req) => {
            expect(interceptFormData(req).file).to.equal('standard_gsc.evf');
            req.reply({
                statusCode: 200,
                body: {
                    type: 'success',
                    object: 'videomodel',
                    category: 'upload',
                    data: {
                        id: 114790101,
                        state: MS_State.Official,
                    },
                },
            });
        }).as('uploadRequest');
        mountAutoUploader({
            participant: weeklyParticipant(),
        });
        setPollInterval(1);

        cy.contains('button', 'Select folder').should('not.be.disabled').click();
        cy.get('@showDirectoryPicker').should('have.been.calledOnce');
        cy.contains('Watching videos').should('be.visible');

        loadStandardGSCFile().then((file) => {
            directory.addFile(file);
        });

        cy.wait('@uploadRequest').its('response.statusCode').should('eq', 200);
        cy.contains('Scanned 1, uploaded 1, skipped 0, failed 0').should('be.visible');
        cy.get('@consoleInfo').should('have.been.calledWithMatch', '[WeeklyAutoUploader]', 'upload success');
        cy.get('@vue').then((wrapper: ComponentWrapper<typeof AutoUploader>) => {
            const emitted = wrapper.emitted('uploaded') ?? [];
            expect(emitted).to.have.length(1);
            expect(emitted[0][0]).to.include({
                id: 114790101,
                state: MS_State.Official,
                level: 'e',
                mode: '00',
                timems: 41021,
            });
        });
    });
});
