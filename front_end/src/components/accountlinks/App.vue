<template>
    <template v-if="store.isSelf || accountlinks.length > 0">
        <el-text tag="b" size="large">
            {{ t('accountlink.title') }}
        </el-text>
        <div v-loading="loading" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(19rem, auto)); grid-gap: 1rem;">
            <template v-for="account in accountlinks" :key="account.platform">
                <card-saolei v-if="account.platform == 'c'" :id="account.identifier" :verified="account.verified" :info="account.data as AccountSaolei" @refresh="refreshAccount(account)" />
                <card-msgames v-else-if="account.platform == 'a'" :id="account.identifier" :verified="account.verified" :info="account.data as AccountMSGames" />
                <card-wo-m v-else-if="account.platform == 'w'" :id="account.identifier" :verified="account.verified" :info="account.data as AccountWoM" @refresh="refreshAccount(account)" />
            </template>
            <card-add v-if="store.player.id == store.user.id && accountlinks.length < 4" :accountlinks="accountlinks" @add-link="addLink" />
        </div>
    </template>
</template>

<script setup lang="ts">
import { ElText, vLoading } from 'element-plus';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import CardAdd from './CardAdd.vue';
import CardMsgames from './CardMsgames.vue';
import CardSaolei from './CardSaolei.vue';
import CardWoM from './CardWoM.vue';
import { AccountLink, AccountMSGames, AccountSaolei, AccountWoM } from './utils';

import { httpErrorNotification } from '@/components/Notifications';
import { store } from '@/store';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const { proxy } = useCurrentInstance();
const { t } = useI18n();

const props = defineProps({
    userId: {
        type: Number,
        default: 0,
    },
});

const loading = ref(false);
const accountlinks = ref<AccountLink[]>([]);

onMounted(refresh);

async function refresh() {
    if (props.userId == 0) return;
    loading.value = true;
    await proxy.$axios.get('accountlink/get/',
        {
            params: {
                id: props.userId,
            },
        },
    ).then(function (response) {
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
    await proxy.$axios.post('accountlink/add/',
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
