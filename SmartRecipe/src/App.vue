<template>
  <v-app>
    <NavBar v-if="!isLoginPage" />
    <v-main>
      <router-view />
    </v-main>
    <v-btn
      v-if="!isLoginPage"
      icon="mdi-robot-outline"
      color="teal"
      size="x-large"
      position="fixed"
      location="bottom right"
      class="ma-4"
      elevation="8"
      style="z-index: 9999;"
      @click="$router.push('/chatbot')"
    ></v-btn>
  </v-app>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const excludedRoutes = ['/login'] 
const isLoginPage = computed(() => excludedRoutes.includes(route.path))
</script>