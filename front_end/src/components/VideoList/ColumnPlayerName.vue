<template>
    <PrColumn min-width="80">
        <template #body="{data}: {data: VideoAbstract}">
            <PlayerName class="name" :user-id="data.player_id" :user-name="data.player_name" />
        </template>
    </PrColumn>
</template>

<script setup lang="ts">

import PrColumn from 'primevue/column';

import PlayerName from '@/components/PlayerName.vue';
import { VideoAbstract } from '@/utils/videoabstract';

</script>
