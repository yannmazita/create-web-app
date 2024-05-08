<template>
    <div class="flex flex-col justify-between h-full max-w-full">
        <div class="flex justify-center">hello</div>
        <ServerInfo></ServerInfo>
    </div>
</template>
<script setup lang="ts">
import { useMenuStore } from '@/stores/menu.ts';
import { onMounted } from 'vue'
import { PageType } from '@/enums.ts';
import ServerInfo from '@/components/BaseServerInfo.vue'

const menuStore = useMenuStore();

onMounted(() => {
    menuStore.setCurrentPage(PageType.HOME);
});
</script>
