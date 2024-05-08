import { defineStore } from 'pinia'
import { reactive } from 'vue'
import { useClientStore } from '@/stores/client.ts';
import { ServerStats } from '@/interfaces.ts';

export const useAppStore = defineStore('app', () => {
    const serverStats: ServerStats = reactive({
        active_users: 0,
    });
    const clientStore = useClientStore();

    async function getServerStats() {
        clientStore.sendSocketMessage(JSON.stringify({
            action: 'server_stats',
        }));
    };

    return {
        serverStats,
        getServerStats,
    }
})

