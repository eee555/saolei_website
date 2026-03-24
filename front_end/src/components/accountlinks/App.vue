<template>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(19rem, auto)); grid-gap: 1rem;">
        <template v-for="account in accountlinks" :key="account.platform">
            <card-saolei v-if="account.platform == 'c'" :id="account.identifier" :verified="account.verified" :info="account.data as AccountSaolei" @refresh="refreshAccount(account)" />
            <card-msgames v-else-if="account.platform == 'a'" :verified="account.verified" :info="account.data as AccountMSGames" />
            <card-wo-m v-else-if="account.platform == 'w'" :id="account.identifier" :verified="account.verified" :info="account.data as AccountWoM" @refresh="refreshAccount(account)" />
        </template>
        <card-add v-if="accountlinks.length < 4" :accountlinks="accountlinks" :disabled="store.player.id != store.user.id" @add-link="addLink" />
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';

import CardAdd from './CardAdd.vue';
import CardMsgames from './CardMsgames.vue';
import CardSaolei from './CardSaolei.vue';
import CardWoM from './CardWoM.vue';
import { AccountLink, AccountMSGames, AccountSaolei, AccountWoM } from './utils';

import { httpErrorNotification } from '@/components/Notifications';
import { store } from '@/store';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const { proxy } = useCurrentInstance();

const props = defineProps({
    userId: {
        type: Number,
        default: 0,
    },
});

const accountlinks = ref<AccountLink[]>([]);

onMounted(refresh);

async function refresh() {
    if (props.userId == 0) return;
    await proxy.$axios.get('accountlink/get/',
        {
            params: {
                id: props.userId,
            },
        },
    ).then(function (response) {
        accountlinks.value = response.data;
    }).catch(httpErrorNotification);
    for (const account of accountlinks.value) {
        refreshAccount(account);
    }
}


function addLink(platform: string, identifier: string) {
    proxy.$axios.post('accountlink/add/',
        {
            platform: platform,
            identifier: identifier,
        },
    ).then(function (_response) {
        refresh();
    }).catch(httpErrorNotification);
}

function refreshAccount(account: AccountLink) {
    if (account.verified) {
        proxy.$axios.get('accountlink/get/', {
            params: {
                id: props.userId,
                platform: account.platform,
            },
        }).then(function (response) {
            account.data = response.data;
        }).catch(httpErrorNotification);
    }
}

</script>
