import { defineStore } from 'pinia';
import { reactive } from 'vue';
import { ServerStats } from '@/interfaces.ts';

export const useServerStore = defineStore('server', () => {
    const serverStats: ServerStats = reactive({
        active_users: 0,
    });

    return {
        serverStats,
    };
});
