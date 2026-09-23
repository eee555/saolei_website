export {};

const STAFF = { id: 1, username: 'staff', password: 'staffPassword' };
const USER = { id: 42, username: 'staff-edit-target' };

interface AdminProfile {
    id: number;
    userms_id: number;
    signature: string;
    is_banned: boolean;
    left_avatar_n: number;
    userms_video_num_limit: number;
}

interface TaskDetail {
    id: string;
    status: string;
    task_path: string;
    args_kwargs: { args: unknown[]; kwargs: Record<string, unknown> };
    run_after: string;
}

describe('Staff requests against the backend', () => {
    it('Before All', () => {
        cy.flushDatabase();
        cy.registerUser(STAFF);
        cy.setStaff(STAFF.id);
        cy.registerUser(USER);
        cy.login(STAFF.username, STAFF.password);
    });

    it('persists UserProfile and UserMS changes submitted from the staff page', () => {
        // Observe real responses; request encoding is validated by the backend.
        cy.intercept('GET', `**/api/userprofile/admin/detail/${USER.id}`).as('loadUser');
        cy.intercept('PATCH', `**/api/userprofile/admin/update/${USER.id}`).as('updateProfile');
        cy.visit('/#/staff/userprofile');
        cy.get('.el-input-number input').clear();
        cy.get('.el-input-number input').type(String(USER.id));
        cy.contains('button', '查询').click();
        cy.wait<unknown, AdminProfile>('@loadUser').then(({ response }) => {
            expect(response?.statusCode).to.eq(200);
            const usermsId = response?.body.userms_id;
            expect(usermsId).to.be.a('number').and.not.eq(USER.id);
            cy.intercept('PATCH', `**/api/msuser/admin/update/${usermsId}`).as('updateUserMS');
        });

        const payload = { signature: '中文 & + =', is_banned: true, left_avatar_n: 0 };
        cy.get('textarea').eq(0).clear();
        cy.get('textarea').eq(0).type(JSON.stringify(payload), { parseSpecialCharSequences: false });
        cy.contains('button', 'PATCH UserProfile').click();
        cy.wait('@updateProfile').its('response.statusCode').should('eq', 200);
        cy.get('textarea').eq(0).should('have.value', '{}');

        cy.contains('button', '查询').click();
        cy.wait('@loadUser').its('response.body').should('include', payload);

        const clearPayload = { signature: '', is_banned: false };
        cy.get('textarea').eq(0).clear();
        cy.get('textarea').eq(0).type(JSON.stringify(clearPayload), { parseSpecialCharSequences: false });
        cy.contains('button', 'PATCH UserProfile').click();
        cy.wait('@updateProfile').its('response.statusCode').should('eq', 200);
        cy.get('textarea').eq(0).should('have.value', '{}');
        cy.contains('button', '查询').click();
        cy.wait('@loadUser').its('response.body').should('include', { ...clearPayload, left_avatar_n: 0 });

        cy.get('textarea').eq(1).clear();
        cy.get('textarea').eq(1).type(JSON.stringify({ video_num_limit: 0 }), { parseSpecialCharSequences: false });
        cy.contains('button', 'PATCH UserMS').click();
        cy.wait('@updateUserMS').its('response.statusCode').should('eq', 200);
        cy.wait('@loadUser').its('response.body.userms_video_num_limit').should('eq', 0);
        cy.get('textarea').eq(1).should('have.value', '{}');
    });

    it('restarts a failed task and deletes it through the staff page', () => {
        cy.dangerzonePost<TaskDetail>('create_failed_task').then(({ body: failedTask }) => {
            cy.intercept('GET', '**/api/common/tasks/detail').as('loadTasks');
            cy.intercept('POST', '**/api/common/tasks/restart').as('restartTask');
            cy.intercept('POST', '**/api/common/tasks/delete').as('deleteTask');
            cy.visit('/#/staff/task');
            cy.contains('button', '加载任务').click();
            cy.wait('@loadTasks').its('response.statusCode').should('eq', 200);
            cy.contains('tr', failedTask.id).contains('button', '重启').click();
            cy.wait<unknown, TaskDetail>('@restartTask').then(({ response }) => {
                expect(response?.statusCode).to.eq(200);
                const restartedTask = response?.body;
                if (!restartedTask) throw new Error('Missing task restart response');
                expect(restartedTask.id).not.to.eq(failedTask.id);
                expect(restartedTask.status).to.eq('READY');
                expect(restartedTask.task_path).to.eq(failedTask.task_path);
                expect(restartedTask.args_kwargs).to.deep.eq(failedTask.args_kwargs);
                expect(restartedTask.run_after).to.eq(failedTask.run_after);
                // Clicking the rightmost action can scroll the ID column out of view.
                cy.contains('td', restartedTask.id).should('exist');

                cy.contains('button', '加载任务').click();
                cy.wait<unknown, TaskDetail[]>('@loadTasks').then(({ response: loaded }) => {
                    expect(loaded?.statusCode).to.eq(200);
                    expect(loaded?.body).to.deep.include(restartedTask);
                    expect(loaded?.body).to.deep.include(failedTask);
                });

                cy.contains('tr', failedTask.id).find('input[type="checkbox"]').check();
                cy.contains('button', '删除选中任务').click();
                cy.wait('@deleteTask').its('response.statusCode').should('eq', 200);
                cy.contains('td', failedTask.id).should('not.exist');
                cy.contains('button', '加载任务').click();
                cy.wait<unknown, TaskDetail[]>('@loadTasks').then(({ response: loaded }) => {
                    expect(loaded?.statusCode).to.eq(200);
                    expect(loaded?.body.map((task) => task.id)).not.to.include(failedTask.id);
                    expect(loaded?.body).to.deep.include(restartedTask);
                });
                cy.contains('td', failedTask.id).should('not.exist');
                cy.contains('td', restartedTask.id).should('exist');
            });
        });
    });
});
