import { defineStore } from 'pinia';
import { reactive, watch } from 'vue';
import { useClientStore } from '@/stores/client.ts';
import { ServerStats } from '@/interfaces.ts';

export const useServerStore = defineStore('server', () => {
    const serverStats: ServerStats = reactive({
        active_users: 0,
    });

    return {
        serverStats,
    };
});
