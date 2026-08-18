const USER = {
    id: 21,
    username: 'weeklyUser',
    email: 'weeklyUser@example.com',
    password: 'weeklyUserPassword',
    realname: '周赛用户',
} as const;

const STAFF = {
    id: 22,
    username: 'weeklyStaff',
    email: 'weeklyStaff@example.com',
    password: 'weeklyStaffPassword',
    realname: '周赛管理员',
} as const;

interface DangerzoneWeeklyTournament {
    id: number;
    start_time: string;
    end_time: string;
}

interface ParticipantWindow {
    startText: string;
    endText: string;
    start: Date;
    end: Date;
}

function pad(value: number) {
    return value.toString().padStart(2, '0');
}

function displayDateTime(date: Date) {
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function parseDisplayDateTime(value: string) {
    const match = (/(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})/).exec(value);
    expect(match, `datetime in ${value}`).to.not.equal(null);
    if (match === null) throw new Error(`datetime not found in ${value}`);
    const [, year, month, day, hour, minute, second] = match;
    return new Date(Number(year), Number(month) - 1, Number(day), Number(hour), Number(minute), Number(second));
}

function createWeeklyTournament(options: {
    year: number;
    week: number;
    startTime: Date;
    endTime: Date;
}) {
    return cy.dangerzonePost<DangerzoneWeeklyTournament>('create_weekly_tournament', {
        year: options.year,
        week: options.week,
        start_time: options.startTime.toISOString(),
        end_time: options.endTime.toISOString(),
        host_id: STAFF.id,
    }).then((response) => response.body);
}

function registerOnTournamentPage(tournamentId: number) {
    cy.intercept('GET', '**/api/tournament/weekly/info*').as('weeklyInfo');
    cy.intercept('POST', '**/api/tournament/weekly/participant').as('createWeeklyParticipant');

    cy.login(USER.username, USER.password);
    cy.visit(`/#/tournament/${tournamentId}`);
    cy.wait('@weeklyInfo').its('response.statusCode').should('eq', 200);

    cy.contains('进行中');
    cy.contains('如何参赛').next().within(() => {
        cy.contains('button', '注册').click();
    });
    cy.wait('@createWeeklyParticipant').its('response.statusCode').should('eq', 200);
    cy.wait('@weeklyInfo').its('response.statusCode').should('eq', 200);

    cy.contains('操作成功');
    cy.closeElNotifications();
    cy.get('[data-cy=weekly-participant-window]').should('be.visible');
}

function getParticipantWindow() {
    return cy.get('[data-cy=weekly-participant-window]').invoke('text').then((text) => {
        const matches = [...text.matchAll(/\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/g)].map((match) => match[0]);
        expect(matches).to.have.length(2);
        return {
            startText: matches[0],
            endText: matches[1],
            start: parseDisplayDateTime(matches[0]),
            end: parseDisplayDateTime(matches[1]),
        };
    });
}

function getVisibleToken() {
    return cy.get('.ttfamily').first().invoke('text').then((text) => text.trim());
}

function readDescriptionValue(label: string) {
    return cy.contains('.el-descriptions__label', label).next().invoke('text').
        then((text) => text.trim());
}

describe('Weekly tournament', () => {
    it('Before All', () => {
        cy.flushDatabase();
        cy.registerUser(USER);
        cy.registerUser(STAFF);
        cy.setStaff(STAFF.id);
    });

    it('registers participants with a two-hour window capped by tournament end time', () => {
        const now = new Date();
        now.setMilliseconds(0);
        const fullWindowStart = new Date(now.getTime() - 60 * 60 * 1000);
        const fullWindowEnd = new Date(now.getTime() + 24 * 60 * 60 * 1000);
        const truncatedStart = new Date(now.getTime() - 60 * 60 * 1000);
        const truncatedEnd = new Date(now.getTime() + 30 * 60 * 1000);
        let tournamentId = 0;

        createWeeklyTournament({
            year: 2099,
            week: 1,
            startTime: fullWindowStart,
            endTime: fullWindowEnd,
        }).then((tournament) => {
            tournamentId = tournament.id;
        });
        cy.then(() => {
            registerOnTournamentPage(tournamentId);
        });
        getParticipantWindow().then((window) => {
            expect(window.end.getTime() - window.start.getTime()).to.equal(2 * 60 * 60 * 1000);
        });

        createWeeklyTournament({
            year: 2099,
            week: 2,
            startTime: truncatedStart,
            endTime: truncatedEnd,
        }).then((tournament) => {
            tournamentId = tournament.id;
        });
        cy.then(() => {
            registerOnTournamentPage(tournamentId);
        });
        getParticipantWindow().then((window) => {
            expect(window.endText).to.equal(displayDateTime(truncatedEnd));
        });
    });

    it('checks in only videos uploaded within the participant window with the participant token', () => {
        const now = new Date();
        now.setMilliseconds(0);
        const tournamentStart = new Date(now.getTime() - 60 * 60 * 1000);
        const tournamentEnd = new Date(now.getTime() + 24 * 60 * 60 * 1000);
        let tournamentId = 0;
        let token = '';
        let participantWindow: ParticipantWindow;

        createWeeklyTournament({
            year: 2099,
            week: 3,
            startTime: tournamentStart,
            endTime: tournamentEnd,
        }).then((tournament) => {
            tournamentId = tournament.id;
        });
        cy.then(() => {
            registerOnTournamentPage(tournamentId);
        });
        getVisibleToken().then((visibleToken) => {
            token = visibleToken;
        });
        getParticipantWindow().then((window) => {
            participantWindow = window;
        });

        cy.then(() => {
            expect(token).to.not.equal('');
            const validUpload = new Date(participantWindow.start.getTime() + 30 * 60 * 1000);
            return cy.createVideo({
                user_id: USER.id,
                identifier: 'weekly-valid',
                tournament_identifier: [token],
                upload_time: validUpload.toISOString(),
                state: 'c',
                level: 'i',
                timems: 12000,
                bv: 80,
            });
        }).then((response) => {
            expect(response.body.id).to.be.greaterThan(0);
            expect(response.body.ongoing_tournament).to.equal(true);
            expect(response.body.tournament_ids).to.include(tournamentId);
        });

        cy.then(() => {
            const validUpload = new Date(participantWindow.start.getTime() + 30 * 60 * 1000);
            return cy.createVideo({
                user_id: USER.id,
                identifier: 'weekly-wrong-token',
                tournament_identifier: ['WRONG_TOKEN'],
                upload_time: validUpload.toISOString(),
                state: 'c',
                level: 'i',
                timems: 13000,
                bv: 80,
            });
        }).then((response) => {
            expect(response.body.id).to.be.greaterThan(0);
            expect(response.body.ongoing_tournament).to.equal(false);
            expect(response.body.tournament_ids).to.not.include(tournamentId);
        });

        cy.then(() => {
            const lateUpload = new Date(participantWindow.end.getTime() + 60 * 1000);
            return cy.createVideo({
                user_id: USER.id,
                identifier: 'weekly-late',
                tournament_identifier: [token],
                upload_time: lateUpload.toISOString(),
                state: 'c',
                level: 'i',
                timems: 14000,
                bv: 80,
            });
        }).then((response) => {
            expect(response.body.id).to.be.greaterThan(0);
            expect(response.body.ongoing_tournament).to.equal(false);
            expect(response.body.tournament_ids).to.not.include(tournamentId);
        });

        cy.intercept('GET', '**/api/tournament/weekly/info*').as('weeklyInfoAfterVideos');
        cy.intercept('GET', '**/api/tournament/get_videos/participant*').as('participantVideos');
        cy.get('[data-cy=weekly-score-refresh]').click();
        cy.wait('@weeklyInfoAfterVideos').its('response.statusCode').should('eq', 200);
        cy.wait('@participantVideos').its('response.statusCode').should('eq', 200);
        cy.contains('.el-tabs__item', '录像').click();
        cy.get('.el-tab-pane:visible').last().within(() => {
            cy.contains('12.000').should('be.visible');
            cy.contains('13.000').should('not.exist');
            cy.contains('14.000').should('not.exist');
        });
    });

    it('lets staff create a weekly tournament and show its finish task in staff tasks', () => {
        let startText = '';
        let endText = '';

        cy.intercept('POST', '**/api/tournament/weekly/new').as('createWeeklyTournament');
        cy.login(STAFF.username, STAFF.password);
        cy.visit('/#/staff/weekly-tournament');
        cy.contains('比赛类型');
        cy.contains('.el-select', '2高5中').should('be.visible');
        cy.contains('button', '创建下周周赛').click();
        cy.wait('@createWeeklyTournament').its('response.statusCode').should('eq', 200);
        cy.contains('操作成功');
        cy.closeElNotifications();
        cy.contains('创建结果');

        readDescriptionValue('开始时间').then((value) => {
            startText = value;
        });
        readDescriptionValue('结束时间').then((value) => {
            endText = value;
        });
        cy.then(() => {
            const start = parseDisplayDateTime(startText);
            const end = parseDisplayDateTime(endText);
            expect(start.getDay()).to.equal(1);
            expect(end.getTime() - start.getTime()).to.equal(7 * 24 * 60 * 60 * 1000);
        });
        cy.intercept('GET', '**/common/staff/taskdetail/').as('taskDetail');
        cy.visit('/#/staff/task');
        cy.contains('button', '加载任务').click();
        cy.wait('@taskDetail').its('response.statusCode').should('eq', 200);
        cy.get('.p-datatable table:visible').getTable().should((tableData) => {
            expect(tableData).to.have.length(1);
            expect(tableData[0].task_path).to.equal('tournament.weekly.tasks.task_weekly_finish');
            expect(tableData[0].run_after).to.equal(endText);
        });
    });
});

export {};
