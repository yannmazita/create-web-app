<template>
    <div class="stats shadow">
        <div class="stat">
            <div class="stat-title">Connected users</div>
            <div class="stat-value">{{ serverStats.active_users }}</div>
            <div class="stat-desc">21% more than last month</div>
        </div>
    </div>
</template>
<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useServerStore } from '@/stores/server.ts';

const serverStore = useServerStore();
const { serverStats } = storeToRefs(serverStore);
</script>
