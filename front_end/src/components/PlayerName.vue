<template>
    <span class="player-name" :title="nameTitle" @click="interactive && $event.stopPropagation()">
        <RouterLink v-if="interactive" :to="playerProfileTo" class="link link--no-underline text">
            <PlayerBadge :user-id="userId" :name="nameShown" :show-avatar="local.playerNameShowAvatar" />
        </RouterLink>
        <PlayerBadge v-else :user-id="userId" :name="nameShown" :show-avatar="local.playerNameShowAvatar" />
    </span>
</template>

<script setup lang="ts" name="PlayerName">
import '@/styles/link.css';
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterLink } from 'vue-router';

import PlayerBadge from '@/components/widgets/PlayerBadge.vue';
import { fetchUserInfo } from '@/services/userService';
import { local } from '@/store/local';
import { formatName } from '@/utils/strings';
import { UserProfile } from '@/utils/userprofile';

const props = defineProps({
    interactive: { type: Boolean, default: true },
    userId: {
        type: Number,
        default: 0,
    },
});

const user = ref(new UserProfile());
const loading = ref(false);
const internationalName = computed(() => {
    const { firstname, lastname } = user.value;
    return firstname && lastname ? formatName(firstname, lastname, local.value.nameFormat) : firstname || lastname;
});
function nameFor(source: typeof local.value.playerName1): string {
    return source === 'international' ? internationalName.value : user.value[source];
}
const nameShown = computed(() => {
    if (props.userId === 0) return '';
    if (user.value.isNameHidden) return `${t('local.user')} #${props.userId}`;
    if (loading.value || user.value.id !== props.userId) return `${t('local.user')}#${props.userId}`;
    const name1 = nameFor(local.value.playerName1) || user.value.username || `${t('local.user')}#${props.userId}`;
    const name2 = nameFor(local.value.playerName2);
    return local.value.playerNameFormat === 'name1 (name2)' && name2 ? `${name1} (${name2})` : name1;
});
const nameTitle = computed(() => (user.value.isNameHidden
    ? nameShown.value
    : [
        `${user.value.username || '--'}#${props.userId}`,
        `${user.value.realname || '--'} (${internationalName.value || '--'})`,
    ].join('\n')));
const playerProfileTo = computed(() => `/player/${props.userId}`);
watch(() => props.userId, async (newVal, _, onCleanup) => {
    let active = true;
    onCleanup(() => {
        active = false;
    });
    user.value = new UserProfile();
    loading.value = newVal !== 0;
    if (newVal === 0) return;
    try {
        const result = await fetchUserInfo(newVal);
        if (active) user.value = result;
    } catch (error) {
        console.log(error);
    } finally {
        if (active) loading.value = false;
    }
}, { immediate: true });

const i18nMessages = {
    'zh-cn': { local: {
        user: '用户',
    } },
    en: { local: {
        user: 'User',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>
