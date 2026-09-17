import CardMineracer from './CardMineracer.vue';
import { mockMineracerResponse, mountAccountLink } from './testUtils';

import { AccountMineracer } from '@/utils/accountlinks';

describe('<CardMineracer />', () => {
    it('renders Mineracer account details', () => {
        mountAccountLink(CardMineracer, {
            id: '123456789',
            info: new AccountMineracer(mockMineracerResponse()),
        });

        cy.contains('Mineracer #123456789');
        cy.contains('2025-05-09 20:13:14');
    });
});
