import { createApp } from 'vue'
import App from './App.vue'
import router from './router'  


import vuetify from './plugins/vuetify'  

import NavBar from './components/navbar.vue' // global component navbar

import { createPinia } from 'pinia' // Add pinia


const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

app.use(router)
app.use(vuetify)
app.component('NavBar', NavBar)

app.mount('#app')