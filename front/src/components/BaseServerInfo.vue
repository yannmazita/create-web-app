<template>
    <div class="collapse collapse-arrow bg-base-200 rounded-none lg:col-start-10 lg:col-end-13">
        <input type="checkbox" />
        <div class="collapse-title text-white text-xl">
            Server information (EU-West)
        </div>
        <div class="collapse-content text-white bg-base-300">
            Online players: {{ activePlayers }}
        </div>
    </div>
</template>
<script setup lang="ts">
import { computed, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useClientStore } from '@/stores/client.ts';

const clientStore = useClientStore();
const { serverStats } = storeToRefs(gameStore);
const { socketMessage } = storeToRefs(clientStore);

const activePlayers = computed(() => {
    return serverStats.value.active_users;
});

watch(socketMessage, (message) => {
    if (message.action === 'server_stats') {
        gameStore.serverStats.active_users = message.data.active_users;
    }
});
</script>
