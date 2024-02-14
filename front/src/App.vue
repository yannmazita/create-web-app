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
import { onMounted } from 'vue';
import { useClientStore } from '@/stores/client.ts';

const clientStore = useClientStore();

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
</script>
