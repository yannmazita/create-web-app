<template>
    <div class="navbar bg-base-300 h-fit w-full">
        <div class="navbar-start">
            <div class="dropdown">
                <div tabindex="0" role="button" class="btn btn-ghost lg:hidden">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4 6h16M4 12h8m-8 6h16" />
                    </svg>
                </div>
                <ul tabindex="0"
                    class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-300 rounded-box w-52">
                    <li><a>Item 1</a></li>
                    <li>
                        <a>Parent</a>
                        <ul class="p-2">
                            <li><a>Submenu 1</a></li>
                            <li><a>Submenu 2</a></li>
                        </ul>
                    </li>
                    <li><a>Item 3</a></li>
                </ul>
            </div>
            <a class="btn btn-ghost text-xl">web-app</a>
        </div>
        <div class="navbar-center hidden lg:flex">
            <ul class="menu menu-horizontal px-1">
                <li><a>Item 1</a></li>
                <li>
                    <details>
                        <summary>Parent</summary>
                        <ul class="p-2">
                            <li><a>Submenu 1</a></li>
                            <li><a>Submenu 2</a></li>
                        </ul>
                    </details>
                </li>
                <li><a>Item 3</a></li>
            </ul>
        </div>
        <div class="navbar-end">
            <router-link to="/" @click="menuStore.resetPage()" v-if="showBackButton"
                class="btn btn-ghost text-2xl xl:text-3xl">↩️</router-link>
            <router-link to="/admin" @click="menuStore.setCurrentPage(PageType.ADMIN)"
                class="btn btn-ghost text-2xl xl:text-3xl">🔒</router-link>
        </div>
    </div>
</template>


<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useMenuStore } from '@/stores/menu.ts';
import { PageType } from '@/enums.ts';

const menuStore = useMenuStore();
const { currentPage } = storeToRefs(menuStore);

const showBackButton = computed(() => {
    return currentPage.value !== PageType.HOME;
});
</script>
