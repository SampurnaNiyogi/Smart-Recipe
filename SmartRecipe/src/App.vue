<template>
  <v-app>
    <!-- Show NavBar only if not on login -->
    <NavBar v-if="!isLoginPage" />
    
    <router-view />
  </v-app>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()

const excludedRoutes = ['/login']

const isLoginPage = computed(() =>
  excludedRoutes.includes(route.path)
)
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()
authStore.init()
</script>
