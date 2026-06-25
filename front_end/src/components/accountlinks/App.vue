<template>
    <div v-loading="loading" class="account-link-main">
        <template v-for="account in accountlinks" :key="account.platform">
            <CardSaolei v-if="account.platform == 'c'" :id="account.identifier" :verified="account.verified" :info="account.data as AccountSaolei" @refresh="refreshAccount(account)" />
            <CardMsgames v-else-if="account.platform == 'a'" :id="account.identifier" :verified="account.verified" :info="account.data as AccountMSGames" />
            <CardWoM v-else-if="account.platform == 'w'" :id="account.identifier" :verified="account.verified" :info="account.data as AccountWoM" @refresh="refreshAccount(account)" />
        </template>
        <CardAdd v-if="store.player.id == store.user.id && accountlinks.length < 4" :accountlinks="accountlinks" @add-link="addLink" />
    </div>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { vLoading } from 'element-plus';
import { ref, watch } from 'vue';

import CardAdd from './CardAdd.vue';
import CardMsgames from './CardMsgames.vue';
import CardSaolei from './CardSaolei.vue';
import CardWoM from './CardWoM.vue';
import type { AccountLink, AccountMSGames, AccountSaolei, AccountWoM } from './utils';

import { httpErrorNotification } from '@/components/Notifications';
import { store } from '@/store';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const props = defineProps({
    userId: {
        type: Number,
        default: 0,
    },
});

const { proxy } = useCurrentInstance();

const loading = ref(false);
const accountlinks = ref<AccountLink[]>([]);

watch(() => props.userId, refresh, { immediate: true });

async function refresh() {
    if (props.userId == 0) return;
    loading.value = true;
    await proxy.$axios.get('accountlink/get/', {
        params: {
            id: props.userId,
        },
    }).then(function (response) {
        accountlinks.value = response.data;
        loading.value = false;
    }).catch(httpErrorNotification);
    for (const account of accountlinks.value) {
        if (account.verified) {
            refreshAccount(account);
        }
    }
}

async function addLink(platform: string, identifier: string) {
    try {
        await proxy.$axios.post('accountlink/add/', {
            platform: platform,
            identifier: identifier,
        });
        await refresh();
    } catch (error) {
        httpErrorNotification(error);
    }
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

<style lang="less" scoped>
.account-link-main {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(19rem, auto));
    grid-gap: 1rem;
}
</style>
