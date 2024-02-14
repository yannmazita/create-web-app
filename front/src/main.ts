import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import './style.css'
import App from '@/App.vue'

import HelloView from '@/views/HelloView.vue'

const pinia = createPinia()
const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '', component: HelloView },
    ]
})

createApp(App).use(router).use(pinia).mount('#app')
