<template>
    <div :class="{ 'horizontal-profile': direction === 'horizontal', 'vertical-profile': direction === 'vertical' }">
        <div class="profile-placeholder">
            <div class="avatar-placeholder">
                <avatar :user-id="store.player.id" />
            </div>
            <div class="info-placeholder">
                <edit-profile v-if="isEditing" @close="isEditing = false" />
                <show-profile v-else @edit="isEditing = true" />
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { PropType, ref } from 'vue';

import Avatar from './Avatar.vue';
import EditProfile from './EditProfile.vue';
import ShowProfile from './ShowProfile.vue';

import { store } from '@/store';

defineProps({
    direction: {
        type: String as PropType<'horizontal' | 'vertical'>,
        default: 'vertical',
    },
});

const isEditing = ref(false);

</script>

<style lang="less" scoped>
.input-label {
    margin-top: 1em;
    margin-bottom: 0.5em;
}

.avatar(@size) {
    width: @size;
    height: @size;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.horizontal-profile {
    padding: 1rem 1.5rem;
    .profile-placeholder {
        display: flex;
        align-items: center;
        gap: 1.2rem;
        border-radius: 2rem;
        .avatar-placeholder {
            .avatar(56px);
        }
        .name {
            font-size: 1.3rem;
        }
    }
}

.vertical-profile {
    padding: 2rem 1.5rem;
    .profile-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        .avatar-placeholder.large {
            .avatar(100px);
        }
        .name {
            font-size: 1.6rem;
        }
    }
}

</style>
