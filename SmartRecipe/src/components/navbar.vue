<template>
  <v-app-bar app color="teal darken-3" dark> 
    <v-toolbar-title>Recipe Manager</v-toolbar-title>
    <v-spacer></v-spacer>

    <template v-if="authStore.isAuthenticated">
      <v-btn text to="/" tag="router-link">Home</v-btn>
      <v-btn text to="/recipes" tag="router-link">Recipes</v-btn> 
      <v-btn text to="/chatbot" tag="router-link">ChatBot</v-btn>
      <v-btn text to="/add" tag="router-link">Add Recipe</v-btn>
       <v-btn icon to="/profile" tag="router-link">
        <v-icon>mdi-account-circle</v-icon>
      </v-btn>
       <v-btn icon @click="handleLogout">
         <v-icon>mdi-logout</v-icon>
       </v-btn>
    </template>

     <template v-else>
       <v-btn text to="/login" tag="router-link">Login</v-btn>
     </template>

  </v-app-bar>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'; // Import store using setup script
import { useRouter } from 'vue-router'; // Import router

const authStore = useAuthStore();
const router = useRouter();

const handleLogout = () => {
  authStore.logout(); // Call the logout action from the store
  router.push('/login'); // Redirect to login page after logout
};
</script>