<template>
    <span @click="interactive && $event.stopPropagation()">
        <a v-if="interactive" :href="playerProfileHref" class="link link--no-underline text">
            <PlayerBadge :user-id="userId" :name="nameShown" />
        </a>
        <PlayerBadge v-else :user-id="userId" :name="nameShown" />
    </span>
</template>

<script setup lang="ts" name="PlayerName">
import '@/styles/link.css';
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import PlayerBadge from '@/components/widgets/PlayerBadge.vue';
import { fetchUserInfo } from '@/services/userService';
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
const nameShown = computed(() => {
    if (loading.value) {
        return `${t('local.user')}#${props.userId}`;
    } else {
        return user.value.realname;
    }
});
const playerProfileHref = computed(() => `#/player/${props.userId}`);
watch(() => props.userId, async (newVal) => {
    user.value = new UserProfile();
    if (newVal === 0) return;
    else {
        loading.value = true;
        try {
            user.value = await fetchUserInfo(props.userId);
            loading.value = false;
        } catch (error) {
            user.value = new UserProfile();
            console.log(error);
        }
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
