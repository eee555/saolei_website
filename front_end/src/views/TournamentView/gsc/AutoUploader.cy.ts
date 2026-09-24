import { interceptFormData } from 'cypress-intercept-formdata';
import { defineComponent, h, ref } from 'vue';

import CommonAutoUploader from '../common/AutoUploader.vue';

import AutoUploaderFilter from './AutoUploaderFilter.vue';

import i18n from '@/i18n';
import { load_video_file } from '@/utils/fileIO';
import type { AnyVideo } from '@/utils/fileIO';
import { MS_Mode, MS_State } from '@/utils/ms_const';
import { TournamentParticipant } from '@/utils/tournaments';
import { VideoAbstract } from '@/utils/videoabstract';
import { FakeDirectoryHandle, setDirectoryPicker, setPollInterval } from '@cy/support/autoUploader';
import { binaryStringToUint8Array } from '@cy/support/stupidCypress';

const AutoUploader = defineComponent({
    props: {
        participant: { type: TournamentParticipant, required: true },
    },
    setup(props) {
        const filter = ref<{ matchesFilter: (video: AnyVideo, stat: VideoAbstract) => boolean }>();
        return () => h(CommonAutoUploader, {
            participant: props.participant,
            filter: (video: AnyVideo, stat: VideoAbstract) => filter.value?.matchesFilter(video, stat) ?? false,
        }, {
            filter: () => h(AutoUploaderFilter, { ref: filter, participant: props.participant }),
        });
    },
});

const avfFixture = 'Exp_FL_35.09_3BV=132_3BVs=3.76_Pu Tian Yi(Hu Bei).avf';

function createParticipant() {
    return new TournamentParticipant({
        token: 'G11479',
        start_time: new Date('2000-01-01T00:00:00Z'),
        end_time: new Date('2099-01-01T00:00:00Z'),
    });
}

function mountUploader(participant: TournamentParticipant) {
    return cy.mount(AutoUploader, { props: { participant }, global: { plugins: [i18n] } });
}

function startWatching(directory: FakeDirectoryHandle, participant: TournamentParticipant) {
    setDirectoryPicker(directory);
    mountUploader(participant);
    setPollInterval(1);
    cy.contains('button', 'Select folder').click();
    cy.contains('.el-dialog button', 'Watch new files only').click();
    cy.contains('Watching videos').should('be.visible');
}

function loadReplay(filename: string) {
    return cy.fixture(filename, 'binary').then((content) => {
        const bytes = binaryStringToUint8Array(content);
        const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;
        return { file: new File([buffer], filename), video: load_video_file(buffer, filename) };
    });
}

describe('<GSC AutoUploader />', () => {
    afterEach(() => {
        setDirectoryPicker();
    });

    it('offers three cumulative filters with the BV filter selected by default', () => {
        mountUploader(createParticipant());
        cy.get('.el-select').should('contain.text', '3BV minimum met').click();
        cy.get('.el-select-dropdown:visible .el-select-dropdown__item').then(($items) => {
            expect($items.toArray().map((item) => item.textContent?.trim())).to.deep.equal([
                'All tournament videos', 'Supported levels and modes', '3BV minimum met',
            ]);
        });
    });

    it('applies the hardcoded GSC stages selected in the component', () => {
        const participant = createParticipant();
        const data = { level: 'e', mode: MS_Mode.Standard, timems: 40000, bv: 100, software: 'e' };
        const stat = new VideoAbstract(data);
        participant.videos = Array.from({ length: 5 }, () => stat);
        let evf: AnyVideo;
        let avf: AnyVideo;
        loadReplay('standard_gsc.evf').then(({ video }) => {
            evf = video;
        });
        loadReplay(avfFixture).then(({ video }) => {
            avf = video;
        });
        mountUploader(participant).then(({ wrapper }) => {
            const filter: (video: AnyVideo, stat: VideoAbstract) => boolean = wrapper.findComponent(CommonAutoUploader).props('filter');
            ['All tournament videos', 'Supported levels and modes', '3BV minimum met'].forEach((label, stage) => {
                cy.get('.el-select').click();
                cy.contains('.el-select-dropdown:visible .el-select-dropdown__item', label).click();
                cy.then(() => {
                    for (const token of ['', 'G114', 'G11479X']) {
                        participant.token = token;
                        expect(filter(evf, stat)).to.equal(false);
                    }
                    participant.token = 'G11479';
                    expect(filter(evf, new VideoAbstract({ ...data, mode: MS_Mode.SpeedNG }))).to.equal(stage === 0);
                    expect(filter(evf, new VideoAbstract({ ...data, level: 'c10_10_10' }))).to.equal(stage === 0);
                    expect(filter(evf, new VideoAbstract({ ...data, bv: 99 }))).to.equal(stage < 2);
                    expect(filter(evf, stat)).to.equal(true);
                    expect(filter(evf, new VideoAbstract({ ...data, timems: 300000 }))).to.equal(true);
                    expect(filter(evf, new VideoAbstract({ ...data, mode: MS_Mode.NoFlag, timems: 39999 }))).to.equal(true);

                    const avfStat = new VideoAbstract({ ...data, software: 'a', timems: 35090 });
                    for (const identifier of ['', `${avf.player_identifier} `, 'Other']) {
                        participant.arbiter_identifier__identifier = identifier;
                        expect(filter(avf, avfStat)).to.equal(false);
                    }
                    participant.arbiter_identifier__identifier = avf.player_identifier;
                    expect(filter(avf, avfStat)).to.equal(true);
                });
            });
        });
    });

    for (const filename of ['standard_gsc.evf', avfFixture]) {
        it(`uploads a matching ${filename.endsWith('.avf') ? 'AVF' : 'EVF'} replay and updates participant videos`, () => {
            const participant = createParticipant();
            const directory = new FakeDirectoryHandle();
            loadReplay(filename).then(({ video }) => {
                if (filename.endsWith('.avf')) {
                    expect(video.player_identifier).not.to.equal('');
                    participant.arbiter_identifier__identifier = video.player_identifier;
                }
            });
            cy.intercept('POST', '/common/uploadvideo/', (req) => {
                expect(interceptFormData(req).file).to.equal(filename);
                req.reply({ body: { type: 'success', object: 'videomodel', category: 'upload', data: { id: 901, state: MS_State.Official } } });
            }).as('upload');
            startWatching(directory, participant);
            loadReplay(filename).then(({ file }) => {
                directory.addFile(file);
            });

            cy.wait('@upload').its('response.statusCode').should('eq', 200);
            cy.contains('Uploaded: 100%(1)').should('be.visible');
            cy.then(() => {
                expect(participant.videos).to.have.length(1);
                expect(participant.videos?.[0]).to.include({ id: 901, state: MS_State.Official });
            });
        });
    }

    it('skips AVF replays without a registered matching identifier', () => {
        const participant = createParticipant();
        const directory = new FakeDirectoryHandle();
        cy.intercept('POST', '/common/uploadvideo/', { statusCode: 500 }).as('upload');
        startWatching(directory, participant);
        loadReplay(avfFixture).then(({ file }) => {
            directory.addFile(file);
        });

        cy.contains('Skipped: 100%(1)').should('be.visible');
        cy.get('@upload.all').should('have.length', 0);
        cy.then(() => expect(participant.videos).to.be.undefined);
    });
});
