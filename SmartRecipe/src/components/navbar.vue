<template>
  <v-app-bar app color="teal darken-3" dark> 
    <v-toolbar-title>Recipe Manager</v-toolbar-title>
    <v-spacer></v-spacer>

    <template v-if="authStore.isAuthenticated">
      <v-btn text to="/" tag="router-link">Home</v-btn>
      <v-btn text to="/recipes" tag="router-link">Recipes</v-btn> 
      <v-btn text to="/my-recipes" tag="router-link">My Recipes</v-btn> 
      <v-btn text to="/add" tag="router-link">Add Recipe</v-btn>
      
      <v-menu offset-y>
        <template v-slot:activator="{ props }">
          <v-btn icon v-bind="props" class="mr-2">
            <v-badge :content="notifications.length" :model-value="notifications.length > 0" color="error">
              <v-icon>mdi-bell</v-icon>
            </v-badge>
          </v-btn>
        </template>
        
        <v-card width="350" max-height="450" class="overflow-y-auto">
          <v-card-title class="d-flex justify-space-between align-center text-subtitle-1 font-weight-bold bg-teal-lighten-5">
            Notifications
            <v-btn size="small" variant="text" color="teal" @click="markAllRead" v-if="notifications.length > 0">Mark all read</v-btn>
          </v-card-title>
          <v-divider></v-divider>
          
          <v-list v-if="notifications.length > 0" lines="three" class="pa-0">
            <v-list-item 
              v-for="notif in notifications" 
              :key="notif.id" 
              @click="goToRecipe(notif.recipe_id)"
              class="border-b"
            >
              <template v-slot:prepend>
                <v-avatar color="teal" class="text-white font-weight-bold mr-3 mt-1">
                  {{ notif.user_name.charAt(0).toUpperCase() }}
                </v-avatar>
              </template>
              <v-list-item-title class="text-wrap" style="line-height: 1.2;">
                <strong>{{ notif.user_name }}</strong> commented on <strong>{{ notif.recipe_name }}</strong>
              </v-list-item-title>
              <v-list-item-subtitle class="mt-1 text-black" style="opacity: 0.85;">
                "{{ notif.text }}"
              </v-list-item-subtitle>
              <v-list-item-subtitle class="text-caption text-teal-darken-2 mt-1">
                {{ new Date(notif.created_at).toLocaleString() }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
          
          <v-card-text v-else class="text-center text-grey pa-6">
            <v-icon size="40" color="grey-lighten-1" class="mb-2">mdi-bell-sleep</v-icon>
            <br>
            You're all caught up!
          </v-card-text>
        </v-card>
      </v-menu>

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
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const notifications = ref([])
let pollInterval = null

// Fetch notifications logic
const fetchNotifications = async () => {
  if (!authStore.isAuthenticated || !authStore.token) return
  try {
    const res = await fetch("http://127.0.0.1:8000/notifications", {
      headers: { "Authorization": `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      notifications.value = await res.json()
    }
  } catch (e) {
    console.error("Failed to load notifications", e)
  }
}

// Mark notifications as read
const markAllRead = async () => {
  if (!authStore.token) return
  try {
    const res = await fetch("http://127.0.0.1:8000/notifications/mark-all-read", {
      method: 'PUT',
      headers: { "Authorization": `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      notifications.value = [] // Clear badge locally immediately
    }
  } catch (e) {
    console.error("Failed to mark notifications read", e)
  }
}

const goToRecipe = (id) => {
  router.push(`/recipe/details/${id}`)
}

const handleLogout = () => {
  authStore.logout()
  notifications.value = []
  router.push('/login')
}

// Set up polling so it checks for new comments automatically
onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchNotifications()
    pollInterval = setInterval(fetchNotifications, 30000) // Poll every 30 seconds
  }
})

watch(() => authStore.isAuthenticated, (newVal) => {
  if (newVal) {
    fetchNotifications()
    if (!pollInterval) pollInterval = setInterval(fetchNotifications, 30000)
  } else {
    notifications.value = []
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>