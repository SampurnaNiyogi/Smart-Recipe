<template>
  <v-app>
    <NavBar v-if="!isLoginPage" />
    <router-view />
  </v-app>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const excludedRoutes = ['/login'] 

const isLoginPage = computed(() => excludedRoutes.includes(route.path))

</script>