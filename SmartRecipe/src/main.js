// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import NavBar from './components/navbar.vue'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/auth' // Import the auth store

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// Initialize auth store AFTER Pinia is used
const authStore = useAuthStore()
authStore.initializeAuth() // <-- ADD THIS LINE to load token from localStorage

app.use(router)
app.use(vuetify)
app.component('NavBar', NavBar)

app.mount('#app')