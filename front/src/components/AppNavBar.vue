<template>
    <div class="navbar bg-base-300 text-base min-h-min w-full py-0">
        <div class="navbar-start">
            <details class="dropdown">
                <summary class="btn btn-ghost">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4 6h16M4 12h8m-8 6h16" />
                    </svg>
                </summary>
                <ul class="menu menu-sm dropdown-content mt-3 z-50 p-2 shadow bg-base-300 rounded-box w-52">
                    <li><router-link to="/a-path" class="text-xl">a link</router-link></li>
                    <li><router-link to="/another-path" class="text-xl">another link</router-link></li>
                </ul>
            </details>
            <router-link to="/" class="btn btn-ghost text-2xl">create-web-app</router-link>
        </div>

        <div class="navbar-center hidden">
            <ul class="menu menu-horizontal px-1">
                <li><router-link to="/a-path" class="text-2xl xl:text-base">a link</router-link></li>
                <li><router-link to="/another-path" class="text-2xl xl:text-base">another link</router-link></li>
            </ul>
        </div>
        <div class="navbar-end">
        </div>
    </div>
</template>


<script setup lang="ts">
</script>
