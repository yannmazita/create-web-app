<template>
    <NavBar />
    <main>
        <div class="flex flex-row flex-nowrap">
            <div class="w-full flex-none">
            </div>
            <div class="w-full flex-none ml-[-100%]">
                <router-view></router-view>
            </div>
        </div>
    </main>
    <AppFooter />
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useClientStore } from '@/stores/client.ts';
import { useServerStore } from '@/stores/server.ts';

const clientStore = useClientStore();
const serverStore = useServerStore();
const { socketMessage } = storeToRefs(clientStore);

onMounted(async () => {
    try {
        await clientStore.connectSocket();
        await clientStore.sendSocketMessage(JSON.stringify({
            action: 'server_stats',
            data: null
        }));
    } catch (error) {
        console.log(error)
    }
});

watch(socketMessage, (newMessage) => {
    if (newMessage.action === 'server_stats') {
        Object.assign(serverStore.serverStats, newMessage.data);
    }
});
</script>
