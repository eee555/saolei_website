import { computed, onActivated, onDeactivated, ref, watch } from 'vue';
import type { ComputedRef, Ref } from 'vue';
import { useRoute } from 'vue-router';

import { profileDataRevision } from '@/services/profileDataService';
import { fetchUserVideos } from '@/services/userService';
import { store } from '@/store';
import { LoginStatus } from '@/utils/common/structInterface';
import type { UserProfile } from '@/utils/userprofile';
import type { VideoAbstract } from '@/utils/videoabstract';

interface ProfileVideosState {
    videos: ComputedRef<VideoAbstract[]>;
    valid: ComputedRef<boolean>;
    loading: Ref<boolean>;
    failed: Ref<boolean>;
    viewerKey: ComputedRef<string>;
    refresh: () => Promise<void>;
}

export function useProfileVideos(user: Ref<UserProfile>): ProfileVideosState {
    const route = useRoute();
    const activated = ref(true);
    onActivated(() => {
        activated.value = true;
    });
    onDeactivated(() => {
        activated.value = false;
    });
    const active = computed(() => activated.value && route.name === 'user-videos' && Number(route.params.id) === user.value.id);
    const viewerKey = computed(() => `${store.login_status}:${store.user.id}:${store.sessionRevision}`);
    const revision = computed(() => profileDataRevision(user.value.id));
    const loading = ref(false);
    const failed = ref(false);
    const valid = computed(() => active.value && user.value.videos !== undefined && user.value.videosViewerKey === viewerKey.value && user.value.videosRevision === revision.value);
    const videos = computed(() => (valid.value ? user.value.videos ?? [] : []));
    let requestNumber = 0;

    async function load(force = false) {
        const number = ++requestNumber;
        loading.value = false;
        failed.value = false;
        if (!active.value || user.value.id < 1 || (store.login_status !== LoginStatus.IsLogin && store.login_status !== LoginStatus.NotLogin)) return;
        if (valid.value && !force) return;
        const owner = user.value;
        const playerId = owner.id;
        const key = viewerKey.value;
        const version = revision.value;
        // Do not leave data obtained under a different identity in the shared profile.
        owner.videos = undefined;
        owner.videosViewerKey = undefined;
        loading.value = true;
        try {
            const result = await fetchUserVideos(playerId, key, version);
            if (owner.id !== playerId || viewerKey.value !== key || profileDataRevision(playerId) !== version) return;
            owner.videos = result;
            owner.videosViewerKey = key;
            owner.videosRevision = version;
        } catch {
            if (number === requestNumber) failed.value = true;
        } finally {
            if (number === requestNumber) loading.value = false;
        }
    }

    watch([active, user, viewerKey, revision], () => {
        void load();
    }, { immediate: true });
    // Cached inactive pages must also discard private data when identity changes.
    watch(viewerKey, () => {
        if (user.value.videosViewerKey !== viewerKey.value) user.value.videos = undefined;
    }, { flush: 'sync' });
    return { videos, valid, loading, failed, viewerKey, refresh: () => load(true) };
}
