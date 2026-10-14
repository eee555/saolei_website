import { ref, watch } from 'vue';
import type { Ref } from 'vue';

import { httpErrorNotification } from '@/components/Notifications';
import { fetchUserInfo } from '@/services/userService';
import { store } from '@/store';

export function usePlayer(userId: () => number): Ref<boolean> {
    const loading = ref(false);

    watch([userId, () => store.user], async ([id], _, onCleanup) => {
        let active = true;
        onCleanup(() => {
            active = false;
        });
        loading.value = false;
        if (!Number.isInteger(id) || id <= 0) return;

        if (id === store.user.id) {
            store.player = store.user;
            return;
        }

        loading.value = true;
        try {
            const player = await fetchUserInfo(id, true);
            // Login or navigation may have changed the player while this request was pending.
            if (active) store.player = player;
        } catch (error) {
            if (active) httpErrorNotification(error);
        } finally {
            if (active) loading.value = false;
        }
    }, { immediate: true });

    return loading;
}
